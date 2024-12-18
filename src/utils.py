import os
import glob
from functools import partial

import pyproj
import numpy as np
import rasterio as rio
import scipy.ndimage as nd
from PIL import Image
from shapely.geometry import Point
from shapely.ops import transform


def area_of_interest(lat, lon, km):
    """
    Generate a buffer around a location (lat, long). Returns
    the geometry corresponding to its spatial envelope.
    """
    proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(lat, lon).buffer(km * 1000)
    aoi = transform(project, buf).exterior.envelope
    xmin, ymin, xmax, ymax = [round(coord, 3) for coord in aoi.bounds]
    return [xmin, ymin, xmax, ymax]


def fill(arr):
    """
    Replace the value of invalid array cells - NaNs
    by the value of the nearest valid array cell.
    """
    ind = nd.distance_transform_edt(np.isnan(arr), return_distances=False, return_indices=True)
    return arr[tuple(ind)]


def rescale(arr, axes=0):
    """
    Scale input array to 0 - 255.
    """
    return ((arr - arr.min()) * (1/(arr.max() - arr.min()) * 255)).astype('uint8')
