import os
import json

import pandas as pd
from shapely.geometry import shape

from src.utils import reproject_geom


class City:
    """Access city-level metadata."""

    def __init__(self, city_name, data_path):
        """
        :param city_name:
            name sub-saharan city to download landsat images
        :param data_path:
            path to city metadata.csv
        """
        self.name = city_name
        self.data_path = data_path
        self.metadata = self.read()

    def read(self):
        """Read CSV metadata file."""
        csv_f = os.path.join(self.data_path, 'metadata.csv')
        return pd.read_csv(csv_f, index_col=0)

    @property
    def epsg(self):
        """Get EPSG code."""
        return str(self.metadata.at[(self.name, 'epsg')])

    @property
    def crs(self):
        """CRS as a dictionnary."""
        return {'init': 'epsg:{}'.format(self.epsg)}

    @property
    def location(self):
        """Latitude & longitude coordinates of the city center."""
        lat = self.metadata.at[(self.name, 'latitude')]
        lon = self.metadata.at[(self.name, 'longitude')]
        return [lat, lon]

    @property
    def aoi(self):
        """Area of interest as a GeoJSON-like dictionnary."""
        path = os.path.join(self.data_path, f'{self.name}_aoi.geojson')
        with open(path) as f:
            geojson = json.load(f)
        return geojson['geometry']

    @property
    def aoi_coordinates(self):
        """Area of interest coordinates, as expected by
        ee.Geometry.Polygon"""
        return self.aoi.get('coordinates')[0]

    @property
    def bbox(self):
        """Get bounding box as list of coordinates, as expected
        by ee.Geometry.Rectangle.
        """
        aoi = reproject_geom(
            shape(self.aoi), src_epsg=self.epsg, dst_epsg=4326)
        xmin, ymin, xmax, ymax = [round(coord, 3) for coord in aoi.bounds]
        return [xmin, ymin, xmax, ymax]
