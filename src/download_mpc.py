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

import test_mosaic

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


def main():
    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    csv = pd.read_csv('data/areas_of_interest.csv', sep=';')
    csv.drop_duplicates(inplace=True)

    df = convert_bbox_to_tuple(csv)

    for cluster in csv['cluster_id']:
        bbox = df[df['cluster_id'] == cluster]['area_of_interest'].values[0]
        year = df[df['cluster_id'] == cluster]['year'].values[0]
        print(cluster, bbox, year)

        test_mosaic.cloudless_mosaic(cluster, bbox, year)


def convert_bbox_to_tuple(df):

    # Convert the area_of_interest column to tuple of floats
    df['area_of_interest'] = df['area_of_interest'].apply(lambda x: tuple(map(float, x.strip('[]').split(','))))

    return df


if __name__ == "__main__":
    main()
