import time

import ee

from src.utils import GoogleEarthEngineDownloadError

ee.Initialize()


class Landsat:
    def __init__(self, country, aoi_coords, start_date, end_date):
        """
        Constructor.

        Parameters
        ----------
        :param aoi_coords: list
            name of country to download satellite data for
        :param aoi_coords: list
            coordinates for area of interest; [xmin, ymin, xmax, ymax]
        :param start_date: str
            start date for filtering a collection by a date range
        :param end_date: str
            end date for filtering a collection by a date range
        """
        self.country = country
        self.aoi_coords = aoi_coords
        self.start_date = start_date
        self.end_date = end_date
        self.rect = ee.Geometry.Rectangle(self.aoi_coords)
        self.coords_json = self.rect.getInfo()['coordinates']
        self.ms_bands = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'TEMP1', 'TEMP2']
        self.done_status = {ee.batch.Task.State.COMPLETED,
                            ee.batch.Task.State.FAILED,
                            ee.batch.Task.State.CANCEL_REQUESTED,
                            ee.batch.Task.State.CANCELLED}

    @staticmethod
    def add_latlon(image):
        """
        :param image: ee.Image
            Landsat8 satellite image

        :returns masked_image: ee.Image
            add bands of longitude and latitude
            coordinates named 'LON' and 'LAT'
        """
        latlon = image.pixelLonLat().select(
            opt_selectors=['longitude', 'latitude'],
            opt_names=['LON', 'LAT'])
        return image.addBands(latlon)

    @staticmethod
    def rename_l8(image):
        """
        :param image: ee.Image
            Landsat8 image

        :returns:
            ee.Image with bands rescaled
        """
        newnames = ['AEROS', 'BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2',
                    'TEMP1', 'TEMP2', 'sr_aerosol', 'pixel_qa', 'radsat_qa']
        return image.rename(newnames)

    @staticmethod
    def rescale_l8(image):
        """
        :param image: ee.Image
                Landsat8 image

        :returns scaled:
                ee.Image with bands rescaled
        """
        opt = image.select(['AEROS', 'BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2'])
        therm = image.select(['TEMP1', 'TEMP2'])
        masks = image.select(['sr_aerosol', 'pixel_qa', 'radsat_qa'])

        opt = opt.multiply(0.0001)
        therm = therm.multiply(0.1)

        scaled = ee.Image.cat([opt, therm, masks]).copyProperties(image)
        # system properties are not copied
        scaled = scaled.set('system:time_start', image.get('system:time_start'))
        return scaled

    @staticmethod
    def decode_qamask(image):
        """
        :param image: ee.Image
            Landsat8 satellite image containing 'pixel_qa' band

        :returns masks: ee.Image
            contains 5 bands of masks
            Pixel QA Bit Flags
            Bit  Attribute
            0    Fill
            1    Clear
            2    Water
            3    Cloud Shadow
            4    Snow
            5    Cloud
        """
        qa = image.select('pixel_qa')
        clear = qa.bitwiseAnd(2).neq(0)  # 0 = not clear, 1 = clear
        clear = clear.updateMask(clear).rename(['pxqa_clear'])

        water = qa.bitwiseAnd(4).neq(0)  # 0 = not water, 1 = water
        water = water.updateMask(water).rename(['pxqa_water'])

        cloud_shadow = qa.bitwiseAnd(8).eq(0)  # 0 = shadow, 1 = not shadow
        cloud_shadow = cloud_shadow.updateMask(cloud_shadow).rename(['pxqa_cloudshadow'])

        snow = qa.bitwiseAnd(16).eq(0)  # 0 = snow, 1 = not snow
        snow = snow.updateMask(snow).rename(['pxqa_snow'])

        cloud = qa.bitwiseAnd(32).eq(0)  # 0 = cloud, 1 = not cloud
        cloud = cloud.updateMask(cloud).rename(['pxqa_cloud'])

        masks = ee.Image.cat([clear, water, cloud_shadow, snow, cloud])
        return masks

    def mask_qaclear(self, image):
        """
        :param image: ee.Image
            Landsat8 satellite image

        :returns masked_image: ee.Image
            input image with cloud-shadow, snow, cloud, and unclear
            pixels masked out
        """
        qam = self.decode_qamask(image)
        cloudshadow_mask = qam.select('pxqa_cloudshadow')
        snow_mask = qam.select('pxqa_snow')
        cloud_mask = qam.select('pxqa_cloud')
        masked_image = (image
                        .updateMask(cloudshadow_mask)
                        .updateMask(snow_mask)
                        .updateMask(cloud_mask))
        return masked_image

    @property
    def composite_nl(self):
        """Creates a median-composite nightlights ee.Image."""

        return (ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
                .filterDate(self.start_date, self.end_date)
                .map(lambda x: x.clip(self.rect))
                .median()
                .select([0], ['NIGHTLIGHTS']))

    @property
    def ms_collection(self):
        """
        Creates an ee.ImageCollection stack or sequence of images
        for aoi between the desired start and end dates.
        """
        return (ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
                .filterDate(self.start_date, self.end_date)
                .map(lambda x: x.clip(self.rect)))

    @property
    def image(self):
        """
        Creates an renamed, rescaled ee.Image with added lon, lat and nightlight bands .
        """
        ms_stack = (self.ms_collection
                    .map(self.rename_l8)
                    .map(self.rescale_l8)
                    .map(self.mask_qaclear)
                    .select(self.ms_bands)
                    .median())
        ms_stack = self.add_latlon(ms_stack)
        ms_stack = ms_stack.addBands(self.composite_nl).toFloat()
        return ms_stack

    def export_image(self, cluster_id):
        """
        Creates a batch task to export an ee.Image as a raster to Google Drive.
        """
        task_config = {
            'description': f'{self.country}_{self.start_date}_{self.end_date}_{cluster_id}',
            'scale': 30,
            'folder': self.country,
            'region': self.coords_json
        }
        task = ee.batch.Export.image.toDrive(self.image, **task_config)
        task.start()
        print(f'>beginning download of landsat image for {self.country} cluster: {cluster_id}')
        while task.status()['state'] != 'COMPLETED':
            print(f">>task status: {task.status()['state']}")
            if task.status()['state'] == 'FAILED':
                raise GoogleEarthEngineDownloadError(task.status()['error_message'])
            time.sleep(3)
        print(f">>task status: {task.status()['state']}")
        print(f'>successfully downloaded data for {self.country} cluster: {cluster_id}, check your Google Drive')
