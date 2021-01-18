import ast
import argparse

import pandas as pd

from src.satellite import Landsat

parser = argparse.ArgumentParser()
parser.add_argument('--country', dest='country', action='store', type=str,
                    help='name of country to download satellite data for')
parser.add_argument('--country_cluster', dest='country_cluster', action='store', type=str,
                    help='path to csv file containing area of interest coordinates for cluster')
parser.add_argument('--start_date', dest='start_date', action='store', type=str,
                    help='start date for filtering ee.ImageCollection by date range, dictated by DHS survey year')
parser.add_argument('--end_date', dest='end_date', action='store', type=str,
                    help='end date for filtering ee.ImageCollection by date range, dictated by DHS survey year')

args = parser.parse_args()

df = pd.read_csv(args.country_cluster)
df['area_of_interest'] = df['area_of_interest'].apply(ast.literal_eval)

for row in df[['cluster_id', 'area_of_interest']].iterrows():
    scene = Landsat(str(args.country), row[1]['area_of_interest'], args.start_date, args.end_date)
    scene.export_image(row[1]['cluster_id'])
