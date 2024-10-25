import numpy as np
import xarray as xr

import rasterio.features
import stackstac
import pystac_client
import planetary_computer

import xrspatial.multispectral as ms
from dask_gateway import GatewayCluster

import matplotlib.pyplot as plt


def main():

    area_of_interest = {
        "type": "Polygon",
        "coordinates": [
            [
                [13.498, -12.386],
                [13.498, -12.314],
                [13.572, -12.314],
                [13.572, -12.386],
                [13.498, -12.386],
            ]
        ],
    }

    # area_of_interest = {
    #     "type": "Polygon",
    #     "coordinates": [
    #         [
    #             [-122.27508544921875, 47.54687159892238],
    #             [-121.96128845214844, 47.54687159892238],
    #             [-121.96128845214844, 47.745787772920934],
    #             [-122.27508544921875, 47.745787772920934],
    #             [-122.27508544921875, 47.54687159892238],
    #         ]
    #     ],
    # }
    # bbox = rasterio.features.bounds(area_of_interest)
    bbox = rasterio.features.bounds(area_of_interest)

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = stac.search(
        bbox=[13.498, -12.386, 13.572, -12.314],
        datetime="2011-01-01/2011-03-31",
        collections=["landsat-c2-l2"],
        query={"eo:cloud_cover": {"lt": 10}},
    )

    items = search.item_collection()
    print(len(items))

    data = (
        stackstac.stack(
            items,
            assets=["red", "green", "blue"],  # red, green, blue
            chunksize=4096,
            resolution=100,
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )

    print(data)

    data = data.persist()

    median = data.median(dim="time").compute()
    print("coucou")

    image = ms.true_color(*median)  # expects red, green, blue DataArrays
    print(image)

    image.plot.imshow()

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
