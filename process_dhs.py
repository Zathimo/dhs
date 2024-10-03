import os
import argparse

import pandas as pd
import geopandas as gpd

from src.utils import area_of_interest
from src.compute_IWI import add_iwi

# this script takes corresponding DHS survey .DTA and .shp files as input.
# It selects out the cluster id and associated wealth index information 
# from the .DTA file and merges it with the latitude and longitude of each
# cluster, found in the .shp file. An area of interest (10x10km) is then
# generated from the coordinates of each cluster. This AOI will be used to
# query GEE for accompanying satellite imagery.

parser = argparse.ArgumentParser()
parser.add_argument('--country', dest='country', action='store', type=str,
                    help='name of surveyed country')
parser.add_argument('--dhs_survey', dest='dhs_survey', action='store', type=str,
                    help='absolute path to dhs survey file')
parser.add_argument('--dhs_gps', dest='dhs_gps', action='store', type=str,
                    help='absolute path to dhs gps file')
parser.add_argument('--buffer', dest='buffer', action='store', type=int,
                    help='size of buffer zone in km')

args = parser.parse_args()
country = args.country
output_path = os.path.join(os.getcwd(), "data", args.country, "dhs")
if not os.path.exists(output_path):
    print(f'creating {output_path}')
    os.makedirs(output_path)

# process DHS survey file, extract mean wealth index for each cluster
df_wealth = pd.read_stata(args.dhs_survey, convert_categoricals=False)
df_wealth.head().to_csv(os.path.join(output_path, 'sample_dhs_survey.csv'), index=False)
df_wealth = (df_wealth[['hv001', 'hv201', 'hv205', 'hv206', 'hv207', 'hv208', 'hv209', 'hv210', 'hv211', 'hv212', 'hv213', 'hv216',
                        'hv221', 'hv243a', 'hv243b', 'hv243d', 'hv243e']]
             .rename(columns={'hv001': 'cluster_id',
                              'hv201': 'water_quality',
                              'hv205': 'toilet_quality',
                              'hv206': 'electricity',
                              'hv207': 'radio',
                              'hv208': 'television',
                              'hv209': 'refrigerator',
                              'hv210': 'bicycle',
                              'hv211': 'motorcycle',
                              'hv212': 'car',
                              'hv213': 'floor_quality',
                              'hv216': 'sleeping_rooms',
                              'hv221': 'telephone',
                              'hv243a': 'mobile_phone',
                              'hv243b': 'watch',
                              'hv243d': 'motorboat',
                              'hv243e': 'computer'
                              })
             .dropna())
df_head = df_wealth.head()
add_iwi(df_head)
print(df_head)
print('extracted and calculated mean wealth index for each cluster')

# process DHS shapefile, extract cluster long, lat
df_geo = (gpd.read_file(args.dhs_gps)[['DHSCLUST', 'LATNUM', 'LONGNUM']]
          .rename(columns={'DHSCLUST': 'cluster_id',
                           'LATNUM': 'latitude',
                           'LONGNUM': 'longitude'}))

# merge cluster wealth index and location information
# calculate area of interest coordinates
output = pd.merge(df_wealth, df_geo, on='cluster_id', how='inner')
# output['area_of_interest'] = output.apply(lambda x: area_of_interest(x['latitude'],
#                                                                      x['longitude'],
#                                                                      args.buffer),
#                                           axis=1)
# print('generated bounding box area of interest around each cluster')

output_dest = os.path.join(output_path, f'raw_{args.country}_cluster_wealth_.csv')
output.to_csv(output_dest, index=False)
print('successfully processed DHS information')
