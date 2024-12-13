import os.path

import numpy as np
import time

import stackstac
import pystac_client
import planetary_computer

import rioxarray


def cloudless_mosaic(cluster_id, bbox, year, output_path, cloud_cover=25):
    # cluster = GatewayCluster

    t = time.time()

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    # Landsat

    search = stac.search(
        bbox=bbox,
        datetime=f"{year}-01-01/{year}-12-31",
        collections=["landsat-c2-l2"],
        query={"eo:cloud_cover": {"lt": cloud_cover}},
    )

    items = search.item_collection()

    return len(items)

    # data = ((
    #             stackstac.stack(
    #                 items,
    #                 bounds_latlon=bbox,
    #                 chunksize=4096,
    #                 resolution=30,
    #                 epsg=3857,
    #             )
    #             .where(
    #                 lambda x: x > 0, other=np.nan
    #             )
    #         ))
    #
    # data = data.persist()
    #
    # median = data.median(dim="time").compute()
    #
    # file_name = f'{cluster_id}.tif'
    # file_path = os.path.join(output_path, file_name)
    # ds = median.to_dataset(dim='band')
    # ds.transpose('band', 'y', 'x').rio.to_raster(file_path)


if __name__ == '__main__':
    print(cloudless_mosaic(1, (13.489, -12.395, 13.581, -12.305), 2011, 'data'))
