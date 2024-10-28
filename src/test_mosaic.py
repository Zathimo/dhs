import numpy as np
import xarray as xr
import time

import rasterio.features
import stackstac
import pystac_client
import planetary_computer

import xrspatial.multispectral as ms
from dask_gateway import GatewayCluster

import matplotlib.pyplot as plt

import rioxarray



def main():
    # cluster = GatewayCluster

    t = time.time()


    bbox = [-122.27508544921875, 47.54687159892238, -121.96128845214844, 47.745787772920934]

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = stac.search(
        bbox=bbox,
        datetime="2020-01-01/2020-12-31",
        collections=["sentinel-2-l2a"],
        query={"eo:cloud_cover": {"lt": 25}},
    )

    items = search.item_collection()
    print("nombre d'items :", len(items))

    data = (
        stackstac.stack(
            items,
            assets=["B04", "B03", "B02"],  # red, green, blue
            bounds_latlon=[-122.27508544921875, 47.54687159892238, -121.96128845214844, 47.745787772920934],
            chunksize=4096,
            resolution=100,
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )

    print(data)

    data = data.persist()

    median = data.median(dim="time").compute()

    image = ms.true_color(*median)  # expects red, green, blue DataArrays
    print(type(image))
    print("temps ecoule :", time.time() - t)

    file_name = 'hello.tif'
    image.transpose('band', 'y', 'x').rio.to_raster(file_name)

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot a dark square
    square = plt.Rectangle((0.25, 0.25), 0.5, 0.5, color='black')
    ax.add_patch(square)

    # Set the limits of the plot
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Display the plot
    plt.show()


if __name__ == '__main__':

    main()

