import time

import ee

ee.Initialize()


class Landsat:
    def __init__(self, city, start_date, end_date):
        """
        Constructor.

        Parameters
        ----------
        :param city: Object
            city-level metadata
        :param start_date: str
            start date for filtering a collection by a date range
        :param end_date: str
            end date for filtering a collection by a date range
        """
        self.city = city
        self.start_date = start_date
        self.end_date = end_date
        self.ms_bands = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'TEMP1', 'TEMP2']
        self.stack = (self.collection('LANDSAT/LC08/C01/T1_SR')
                      .map(self.rename_l8)
                      .map(self.rescale_l8)
                      .map(self.mask_qaclear)
                      .select(self.ms_bands)
                      .median())

    def collection(self, name):
        """
        Creates an ee.ImageCollection stack or sequence of images
        for aoi between the desired start and end dates.

        Args:
            :param name: str
                name of image collection
        Returns:
            :returns iee.ImageCollection:
                an ImageCollection stack or sequence of images
        """
        return (ee.ImageCollection(name)
                .filterBounds(ee.Geometry.Rectangle(self.city.bbox))
                .filterDate(self.start_date, self.end_date))

    @staticmethod
    def rename_l8(image):
        """
        Args:
            :param image: ee.Image
                landsat8 image

        Returns:
            :returns:
                ee.Image with bands rescaled
        """
        newnames = ['AEROS', 'BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2',
                    'TEMP1', 'TEMP2', 'sr_aerosol', 'pixel_qa', 'radsat_qa']
        return image.rename(newnames)

    @staticmethod
    def rescale_l8(image):
        """
        Args:
            :param image: ee.Image
                landsat8 image
        Returns:
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
        Args:
            :param image: ee.Image
                Landsat satellite image containing 'pixel_qa' band

        Returns:
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
        Args:
            :param image: ee.Image
                Landsat satellite image

        Returns:
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

    def export_image(self):
        """
        Creates a batch task to export an Image as a raster to Google Drive.
        """
        task_config = {
            'description': f'{self.city.name}_{self.start_date}_{self.end_date}_1',
            'scale': 30,
            'folder': self.city.name,
            'region': ee.Geometry.Rectangle(self.city.bbox).getInfo()['coordinates']
        }
        task = ee.batch.Export.image.toDrive(self.stack, **task_config)
        task.start()
        print(f'>beginning download of landsat image for {self.city.name}')
        while task.status()['state'] != 'COMPLETED':
            print(f">>task status: {task.status()['state']}")
            time.sleep(3)
        print(f">>task status: {task.status()['state']}")
        print(f'>successfully downloaded data for {self.city.name}, check your Google Drive')
