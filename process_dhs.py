import os
import argparse

import pandas as pd
import geopandas as gpd

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
df_wealth = (df_wealth[['hhid', 'hv001']]
             .rename(columns={'hhid': 'HHID',
                              'hv001': 'cluster_id',
                              })
             .dropna())
print(type(df_wealth['HHID'][1]))

# process DHS shapefile, extract cluster long, lat
df_geo = (gpd.read_file(args.dhs_gps)[['DHSCLUST', 'LATNUM', 'LONGNUM']]
          .rename(columns={'DHSCLUST': 'cluster_id',
                           'LATNUM': 'lat',
                           'LONGNUM': 'lon'}))

# merge cluster wealth index and location information
# calculate area of interest coordinates
output = pd.merge(df_wealth, df_geo, on='cluster_id', how='inner')

output['area_of_interest'] = output.apply(lambda x: area_of_interest(x['lat'],
                                                                     x['lon'],
                                                                     args.buffer),
                                          axis=1)
print('generated bounding box area of interest around each cluster')

print(output.head())

# add IWI to the dataset
df_iwi, meta = pyreadstat.read_sav('data/Angola2011-addIWI.sav')
df_iwi = df_iwi[['HHID', 'iwi']].rename(columns={'iwi': 'iwi_smits'})

output = pd.merge(output, df_iwi, on='HHID', how='inner')

output_dest = os.path.join(output_path, f'raw_{args.country}_cluster_wealth_.csv')

output.to_csv(output_dest, index=False, sep=';')
print('successfully processed DHS information')
