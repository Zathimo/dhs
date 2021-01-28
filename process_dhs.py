import os
import argparse

import pandas as pd
import geopandas as gpd

from src.utils import area_of_interest

# this script takes both a DHS survey .DTA and .shp file as input.
# It selects the cluster id and associated wealth index information.
# This information is then merged with the latitude and longitude of
# each cluster. An area of interest (10x10km) is then generated from
# the latitude and longitude of each cluster.

parser = argparse.ArgumentParser()
parser.add_argument('--country', dest='country', action='store',
                    help='name of surveyed country')
parser.add_argument('--dhs_survey', dest='dhs_survey', action='store',
                    help='absolute path to dhs survey file')
parser.add_argument('--dhs_gps', dest='dhs_gps', action='store',
                    help='absolute path to dhs gps file')
parser.add_argument('--dhs_output', dest='dhs_output', action='store',
                    help='absolute path to dhs.csv output file: e.g "./data/dhs/"')

args = parser.parse_args()

# process DHS survey file, extract median wealth index for each cluster
df_wealth = pd.read_stata(args.dhs_survey, convert_categoricals=False)
df_wealth = (df_wealth[['hv001', 'hv271']]
             .rename(columns={'hv001': 'cluster_id',
                              'hv270': 'wealth_category',
                              'hv271': 'wealth_index'})
             .dropna())
df_wealth['wealth_index'] = df_wealth['wealth_index'] / 100000.0
df_cluster_wealth = df_wealth.groupby('cluster_id').mean().reset_index()

# process DHS shapefile, extract cluster long, lat
df_geo = (gpd.read_file(args.dhs_gps)[['DHSCLUST', 'LATNUM', 'LONGNUM']]
          .rename(columns={'DHSCLUST': 'cluster_id',
                           'LATNUM': 'latitude',
                           'LONGNUM': 'longitude'}))

# merge cluster wealth index and location information
# calculate area of interest coordinates
output = pd.merge(df_cluster_wealth, df_geo, on='cluster_id', how='inner')
output['area_of_interest'] = output.apply(lambda x: area_of_interest(x['latitude'], x['longitude'], 5), axis=1)
output_dest = os.path.join(args.dhs_output, f'{args.country}_cluster_wealth.csv')
output.to_csv(output_dest, index=False)
