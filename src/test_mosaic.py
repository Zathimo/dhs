import numpy as np
import time

import stackstac
import pystac_client
import planetary_computer

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
        datetime="2009-01-01/2011-12-31",
        collections=["landsat-c2-l2"],
        query={"eo:cloud_cover": {"lt": 25}},
    )

    items = search.item_collection()
    print("nombre d'items :", len(items))

    data = ((
                stackstac.stack(
                    items,
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

    print(median)

    file_name = f'data/landsat_red.tif'
    ds = median.to_dataset(dim='band')
    ds.transpose('band', 'y', 'x').rio.to_raster(file_name)


if __name__ == '__main__':
    main()
