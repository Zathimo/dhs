import os

import pandas as pd
import geopandas as gpd

import src.process_IWI as iwi
from src.utils import area_of_interest
import pyreadstat

from src.process_IWI import read_petterson, read_sustain_bench


# this script takes corresponding DHS survey .DTA and .shp files as input.
# It selects out the cluster id and associated wealth index information 
# from the .DTA file and merges it with the latitude and longitude of each
# cluster, found in the .shp file. An area of interest (10x10km) is then
# generated from the coordinates of each cluster. This AOI will be used to
# query GEE for accompanying satellite imagery.


def main(folder_path, country, year, buffer):
    output_path = os.path.join(os.getcwd(), "data", "dhs")

    if not os.path.exists(output_path):
        print(f'creating {output_path}')
        os.makedirs(output_path)

    folder = os.path.join(folder_path, year)

    dhs_survey = None
    dhs_gps = None
    dhs_iwi = None

    for file_name in os.listdir(folder):
        if file_name.endswith('.DTA'):
            dhs_survey = os.path.join(folder, file_name)
            print("dhs_survey:", file_name)
        if file_name.endswith('.shp'):
            dhs_gps = os.path.join(folder, file_name)
            print("dhs_gps:", file_name)
        if file_name.endswith('.sav'):
            dhs_iwi = os.path.join(folder, file_name)
            print("dhs_iwi:", file_name)

    if not dhs_survey or not dhs_gps or not dhs_iwi:
        print(f"Skipping {folder}")
        return

    #####################################################################
    # Process DHS survey file, extract mean wealth index for each cluster
    #####################################################################

    df_survey = pd.read_stata(dhs_survey, convert_categoricals=False)
    df_survey['country'] = country
    df_survey = (df_survey[['country', 'hv007', 'hhid', 'hv001', 'hv025']]
                 .rename(columns={'hv007': 'year',
                                  'hhid': 'HHID',
                                  'hv001': 'cluster_id',
                                  'hv025': 'urban_rural',
                                  })
                 .dropna())

    df_survey['HHID'] = df_survey['HHID'].astype(str).str.strip()

    if df_survey['year'].astype(int)[0] < 100:
        df_survey['year'] = df_survey['year'].astype(int) + 1900

    print('Selected DHS columns.')

    ##################################################
    # Process DHS shapefile, extract cluster long, lat
    ##################################################

    df_geo = (gpd.read_file(dhs_gps)[['DHSCLUST', 'LATNUM', 'LONGNUM']]
              .rename(columns={'DHSCLUST': 'cluster_id',
                               'LATNUM': 'lat',
                               'LONGNUM': 'lon'}))

    # merge cluster wealth index and location information
    dhs_geo = pd.merge(df_survey, df_geo, on='cluster_id', how='inner')

    # calculate area of interest coordinates
    dhs_geo['area_of_interest'] = dhs_geo.apply(lambda x: area_of_interest(x['lat'],
                                                                           x['lon'],
                                                                           buffer),
                                                axis=1)

    dhs_geo.to_csv(os.path.join(output_path, f'geo_survey/{country}_{year}_cluster_wealth.csv'), index=False, sep=';')

    print('Generated bounding box area of interest around each cluster.')

    ########################
    # Add IWI to the dataset
    ########################

    if dhs_iwi:
        output = iwi.get_IWI_global(dhs_geo, dhs_iwi)
    else:
        output = iwi.get_IWI_petterson(dhs_geo)

    output_dest = os.path.join(os.getcwd(), "data", "dhs", f'{country}_{year}.csv')

    output.to_csv(output_dest, index=False, sep=';')
    print('successfully processed DHS information')

    return output


if __name__ == '__main__':
    buffer = 5
    df_global = pd.read_csv('data/global_data_lab_only.csv')
    df_global['lat'] = df_global['lat'].round(6)
    df_global['lon'] = df_global['lon'].round(6)

    df_petterson = read_petterson()
    df_sustain = read_sustain_bench()


    df_all = pd.concat([df_global, df_petterson, df_sustain])

    df_all.drop_duplicates(['lat', 'lon'], inplace=True)
    df_all.drop(['iwi'], axis=1, inplace=True)

    df_all['area_of_interest'] = df_all.apply(lambda x: area_of_interest(x['lat'],
                                                                         x['lon'],
                                                                         buffer),
                                              axis=1)

    df_all['country'] = df_all['country'].str.lower()

    df_all.sort_values(['country', 'year'], inplace=True)

    df_all.to_csv('data/areas_of_interest.csv', index=False, sep=';')
