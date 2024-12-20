import os.path

import numpy as np
import time

from datetime import datetime, timedelta

import stackstac
import pystac_client
import planetary_computer

import rioxarray


def cloudless_mosaic(cluster_id, bbox, year, month, output_path, cloud_cover=25, time_span=2, epsg=3857):
    # cluster = GatewayCluster

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    # Landsat

    date_min, date_max = compute_time_frame_centered(f"{year}-{month}-01", 365*time_span)

    print(f"{date_min}/{date_max}")

    search = stac.search(
        bbox=bbox,
        datetime=f"{date_min}/{date_max}",
        collections=["landsat-c2-l2"],
        query={"eo:cloud_cover": {"lt": cloud_cover}},
    )

    items = search.item_collection()

    print(items[:])

    data = ((
                stackstac.stack(
                    items,
                    bounds_latlon=bbox,
                    chunksize=4096,
                    resolution=30,
                    epsg=epsg,
                )
                .where(
                    lambda x: x > 0, other=np.nan
                )
            ))

    data = data.persist()

    median = data.median(dim="time").compute()

    file_name = f'{cluster_id}.tif'
    file_path = os.path.join(output_path, file_name)
    ds = median.to_dataset(dim='band')
    print(ds)
    ds.transpose('band', 'y', 'x').rio.to_raster(file_path)

    return items


def compute_time_frame_centered(date_str, time_frame_days):
    # Convert the date string to a datetime object
    center_date = datetime.strptime(date_str, '%Y-%m-%d')

    # Compute the start and end dates
    start_date = center_date - timedelta(days=time_frame_days // 2)
    end_date = center_date + timedelta(days=time_frame_days // 2)

    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


if __name__ == '__main__':
    print(cloudless_mosaic(292, (13.489, -12.395, 13.581, -12.305), 2006, 1, 'data'))
