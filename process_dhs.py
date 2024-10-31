import os
import argparse

import pandas as pd
import geopandas as gpd

import src.process_IWI as iwi
from src.utils import area_of_interest
import pyreadstat

# this script takes corresponding DHS survey .DTA and .shp files as input.
# It selects out the cluster id and associated wealth index information 
# from the .DTA file and merges it with the latitude and longitude of each
# cluster, found in the .shp file. An area of interest (10x10km) is then
# generated from the coordinates of each cluster. This AOI will be used to
# query GEE for accompanying satellite imagery.

parser = argparse.ArgumentParser()
parser.add_argument('--country', dest='country', action='store', type=str,
                    help='name of surveyed country')
parser.add_argument('--year', dest='year', action='store', type=str,
                    help='year of survey')
parser.add_argument('--dhs_survey', dest='dhs_survey', action='store', type=str,
                    help='absolute path to dhs survey file')
parser.add_argument('--dhs_gps', dest='dhs_gps', action='store', type=str,
                    help='absolute path to dhs gps file')
parser.add_argument('--buffer', dest='buffer', action='store', type=int,
                    help='size of buffer zone in km')


def main(country, year, buffer):
    output_path = os.path.join(os.getcwd(), "data", "dhs")
    if not os.path.exists(output_path):
        print(f'creating {output_path}')
        os.makedirs(output_path)

    folder = os.path.join('data', country, year)
    dhs_survey = None
    dhs_gps = None
    dhs_iwi = None

    for file_name in os.listdir(folder):
        if file_name.endswith('.DTA'):
            dhs_survey = os.path.join(folder, file_name)
            print("dhs_survey", file_name)
        if file_name.endswith('.shp'):
            dhs_gps = os.path.join(folder, file_name)
            print("dhs_gps", file_name)
        if file_name.endswith('.sav'):
            dhs_iwi = os.path.join(folder, file_name)
            print("dhs_iwi", file_name)

    #####################################################################
    # Process DHS survey file, extract mean wealth index for each cluster
    #####################################################################

    df_wealth = pd.read_stata(dhs_survey, convert_categoricals=False)
    df_wealth['country'] = country
    df_wealth = (df_wealth[['country', 'hv007', 'hhid', 'hv001']]
                 .rename(columns={'hv007': 'year',
                                  'hhid': 'HHID',
                                  'hv001': 'cluster_id',
                                  })
                 .dropna())

    print('Selected DHS columns.')

    ##################################################
    # Process DHS shapefile, extract cluster long, lat
    ##################################################

    df_geo = (gpd.read_file(dhs_gps)[['DHSCLUST', 'LATNUM', 'LONGNUM']]
              .rename(columns={'DHSCLUST': 'cluster_id',
                               'LATNUM': 'lat',
                               'LONGNUM': 'lon'}))

    # merge cluster wealth index and location information
    dhs_geo = pd.merge(df_wealth, df_geo, on='cluster_id', how='inner')

    # calculate area of interest coordinates
    dhs_geo['area_of_interest'] = dhs_geo.apply(lambda x: area_of_interest(x['lat'],
                                                                           x['lon'],
                                                                           buffer),
                                                axis=1)

    print('Generated bounding box area of interest around each cluster.')

    ########################
    # Add IWI to the dataset
    ########################

    if dhs_iwi:
        output = iwi.get_IWI_global(dhs_geo, dhs_iwi)
    else:
        output = iwi.get_IWI_petterson(dhs_geo)

    output_dest = os.path.join(output_path, f'{country}_{year}.csv')

    output.to_csv(output_dest, index=False, sep=';')
    print('successfully processed DHS information')


if __name__ == '__main__':
    buffer = 5

    # for folder_name in os.listdir('data'):
    #     folder_path = os.path.join('data', folder_name)
    #     if os.path.isdir(folder_path):
    #         for subfolder_name in os.listdir(folder_path):
    #            main(folder_path, subfolder_name, buffer)

    if os.path.isdir('data/angola'):
        for subfolder_name in os.listdir('data/angola'):
            main('angola', subfolder_name, buffer)
