import pystac_client
import requests
import planetary_computer
from pystac_client.stac_api_io import StacApiIO
import pandas as pd

from urllib3 import Retry
from urllib.parse import urlparse

from torchgeo.datasets.utils import download_url
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import scipy.stats

import rasterio
from rasterio import windows
from rasterio import warp

import numpy as np
from PIL import Image

import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


def main():
    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    csv = pd.read_csv('../data/Angola/dhs/raw_angola_cluster_wealth_.csv', sep=';')
    csv.drop_duplicates(inplace=True)
    csv = csv.head()
    print(csv)

    for cluster in [1]:
        df = convert_bbox_to_tuple(csv)
        bbox = df['area_of_interest'][0]
        time_of_interest = "2020-01-01/2020-12-31"

        search = stac.search(
            collections=["landsat-c2-l2"],
            bbox=bbox,
            datetime=time_of_interest,
            query={"eo:cloud_cover": {"lt": 10}},
        )

        items = search.item_collection()

        selected_item = min(items, key=lambda item: item.properties["eo:cloud_cover"])

        signed_item = planetary_computer.sign(selected_item)

        for band in signed_item.assets.keys():

            asset_href = signed_item.assets[band].href
            try:

                with rasterio.open(asset_href) as ds:
                    warped_aoi_bounds = warp.transform_bounds("epsg:4326", ds.crs, *bbox)
                    aoi_window = windows.from_bounds(transform=ds.transform, *warped_aoi_bounds)
                    band_data = ds.read(window=aoi_window)


                    file_name = 'angola_cluster_' + str(cluster) + '_' + band + '.tif'
                    img = Image.fromarray(band_data[0])
                    img.save(file_name)
            except Exception:
                print("Band failed to save: ", band)




def convert_bbox_to_tuple(df):

    # Convert the area_of_interest column to tuple of floats
    df['area_of_interest'] = df['area_of_interest'].apply(lambda x: tuple(map(float, x.strip('[]').split(','))))

    return df


if __name__ == "__main__":
    main()
