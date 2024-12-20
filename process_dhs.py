import os

import pandas as pd
import geopandas as gpd
from math import isnan

import src.process_IWI as iwi
from src.utils import area_of_interest
import pyreadstat

from src.process_IWI import read_petterson, read_sustain_bench, get_all_aoi


# this script takes corresponding DHS survey .DTA and .shp files as input.
# It selects out the cluster id and associated wealth index information 
# from the .DTA file and merges it with the latitude and longitude of each
# cluster, found in the .shp file. An area of interest (10x10km) is then
# generated from the coordinates of each cluster. This AOI will be used to
# query GEE for accompanying satellite imagery.


def main(folder_path, country, year, buffer):
    output_path = os.path.join(os.getcwd(), "data", "dhs_month")

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
    df_survey = (df_survey[['country', 'hv006', 'hv007', 'hhid', 'hv001', 'hv025']]
                 .rename(columns={'hv006': 'month',
                                  'hv007': 'year',
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

    output_dest = os.path.join(os.getcwd(), "data", "dhs_month", f'{country}_{year}.csv')

    output.to_csv(output_dest, index=False, sep=';')
    print('successfully processed DHS information')

    return output


def process_all_dhs_files(buffer=5):
    for folder_name in os.listdir('data'):
        folder_path = os.path.join('data', folder_name)
        if os.path.isdir(folder_path):
            for subfolder_name in os.listdir(folder_path):
                try:
                    main(folder_path, folder_name, subfolder_name, buffer)
                except Exception as e:
                    print(f'Error processing {folder_path}/{subfolder_name}: {e}')
                    continue


def build_global_data_lab_only(folder_path):
    output = pd.DataFrame([])
    print(output)
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(folder_path, file), sep=';')
            output = pd.concat([output, df])
            output = output[output['lat']!=0]
    output.to_csv(os.path.join(folder_path, 'global_data_lab.csv'), sep=';', index=False)



if __name__ == '__main__':
    get_all_aoi(5)

