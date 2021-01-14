import argparse
import pandas as pd
import geopandas as gpd

from src.utils import area_of_interest

parser = argparse.ArgumentParser()
parser.add_argument('--dhs_survey', dest='dhs_survey', action='store',
                    help='absolute path to dhs survey file')
parser.add_argument('--dhs_gps', dest='dhs_gps', action='store',
                    help='absolute path to dhs gps file')

args = parser.parse_args()

df_wealth = pd.read_stata(args.dhs_survey)
df_wealth = (df_wealth[['hv001', 'hv271']]
             .rename(columns={'hv001': 'cluster_id',
                              'hv270': 'wealth_category',
                              'hv271': 'wealth_index'})
             .dropna())
df_wealth['wealth_index'] = df_wealth['wealth_index'] / 100000.0
df_cluster_wealth = df_wealth.groupby('cluster_id').median().reset_index()

df_geo = (gpd.read_file(args.dhs_gps)[['DHSCLUST', 'LATNUM', 'LONGNUM']]
          .rename(columns={'DHSCLUST': 'cluster_id',
                           'LATNUM': 'latitude',
                           'LONGNUM': 'longitude'}))
output = pd.merge(df_cluster_wealth, df_geo, on='cluster_id', how='inner')
output['area_of_interest'] = output.apply(lambda x: area_of_interest(x['latitude'], x['longitude'], 5), axis=1)
output.to_csv('/Users/Patrick/workspace/landsat-city/data/rwanda_2014_15/dhs/rwanda_cluster_wealth.csv', index=False)