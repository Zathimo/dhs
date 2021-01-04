from functools import partial

import pyproj
from shapely.ops import transform


def reproject_geom(geom, src_epsg, dst_epsg):
    """Re-project a shapely geometry given a source EPSG and a
    target EPSG.
    """
    src_proj = pyproj.Proj(init='epsg:{}'.format(src_epsg))
    dst_proj = pyproj.Proj(init='epsg:{}'.format(dst_epsg))
    reproj = partial(pyproj.transform, src_proj, dst_proj)
    return transform(reproj, geom)
