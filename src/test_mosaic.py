import numpy as np
import time

import stackstac
import pystac_client
import planetary_computer

import xrspatial.multispectral as ms

import matplotlib.pyplot as plt

import rioxarray


def main():
    # cluster = GatewayCluster

    t = time.time()

    bbox = (-122.27508544921875, 47.54687159892238, -121.96128845214844, 47.745787772920934)

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    # Landsat

    search = stac.search(
        bbox=bbox,
        datetime="2020-01-01/2020-12-31",
        collections=["landsat-c2-l2"],
        query={"eo:cloud_cover": {"lt": 25}},
    )

    items = search.item_collection()
    print("nombre d'items :", len(items))

    data = ((
                stackstac.stack(
                    items,
                    assets=["red", "green", "blue"],
                    bounds_latlon=bbox,
                    chunksize=4096,
                    resolution=30,
                )
                .where(
                    lambda x: x > 0, other=np.nan
                )
            ))
    print(data)

    data = data.persist()

    median = data.median(dim="time").compute()

    landsat_image = ms.true_color(*median)[..., :3]  # expects red, green, blue DataArrays
    print('Landsat image:', landsat_image)
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_axis_off()
    landsat_image.plot.imshow(ax=ax)
    print("temps ecoule :", time.time() - t)

    # Display the plot
    plt.show()

    file_name = 'cloudless_landsat.tif'
    landsat_image.transpose('band', 'y', 'x').rio.to_raster(file_name)


if __name__ == '__main__':
    main()
