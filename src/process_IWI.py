import pandas as pd
import numpy as np
from math import isnan

import matplotlib.pyplot as plt
import scipy.stats
import pyreadstat
from sklearn.metrics import r2_score
from src.utils import area_of_interest

import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

CNAMES = {'AO': 'Angola', 'BJ': 'Benin', 'BF': 'Burkina_Faso', 'BU': 'Burundi', 'CA': 'Cameroon',
          'CF': 'Central_African_Republic', 'TD': 'Chad', 'KM': 'Comoros', 'CI': 'Cote_dIvoire',
          'CD': 'Congo_Democratic_Republic', 'SZ': 'Eswatini', 'ET': 'Ethiopia', 'GA': 'Gabon', 'GM': 'Gambia',
          'GH': 'Ghana', 'GN': 'Guinea', 'KE': 'Kenya', 'LS': 'Lesotho', 'LB': 'Liberia', 'MD': 'Madagascar',
          'MW': 'Malawi', 'ML': 'Mali', 'MZ': 'Mozambique', 'NM': 'Namibia', 'NI': 'Niger',
          'NG': 'Nigeria', 'RW': 'Rwanda', 'SL': 'Sierra_Leone', 'ZA': 'South_Africa', 'SN': 'Senegal',
          'TZ': 'Tanzania',
          'TG': 'Togo',
          'ZM': 'Zambia', 'ZW': 'Zimbabwe'}


def read_IWI(input_path, output_path):
    df, meta = pyreadstat.read_sav(input_path)

    df.to_csv(output_path, index=False)
    output = pd.read_csv(output_path, sep=',')

    return output


def read_global_data_lab():
    df = pd.read_csv('data/global_data_lab_only.csv')
    df['urban_rural'] = df['urban_rural'].map({1: 'U', 2: 'R'})

    df['lat'] = df['lat'].round(6)
    df['lon'] = df['lon'].round(6)

    return df


def read_sustain_bench():
    df = pd.read_csv('data/dhs_final_labels.csv')[['cname', 'year', 'cluster_id', 'urban', 'lat', 'lon', 'asset_index']]
    df = df[df['cname'].isin(CNAMES.keys())].rename(columns={'cname': 'country'})
    df['country'] = df['country'].map(CNAMES)
    df.rename(columns={'asset_index': 'iwi'}, inplace=True)

    df.rename(columns={'urban': 'urban_rural'}, inplace=True)

    df['lat'] = df['lat'].round(6)
    df['lon'] = df['lon'].round(6)

    return df


def read_petterson():
    df = pd.read_csv('data/dhs_clusters_rounded.csv')[['country', 'year', 'rural', 'lat', 'lon', 'iwi']]
    df.rename(columns={'rural': 'urban_rural'}, inplace=True)
    df['urban_rural'] = df['urban_rural'].map({0: 'U', 1: 'R'})

    df['lat'] = df['lat'].round(6)
    df['lon'] = df['lon'].round(6)

    return df


def get_IWI_petterson(df):
    df.drop_duplicates('cluster_id', inplace=True)
    df.drop(columns=['HHID'], inplace=True)
    df_iwi = pd.read_csv('data/dhs_clusters.csv', sep=',')
    df_iwi = df_iwi[['lat', 'lon', 'iwi']]

    df_iwi['lat'] = df_iwi['lat'].round(6)
    df_iwi['lon'] = df_iwi['lon'].round(6)

    output = pd.merge(df, df_iwi, on=['lat', 'lon'], how='inner')

    return output


def calculate_mean_iwi_per_cluster(df):
    # Group by cluster_id and calculate the mean IWI
    mean_iwi_per_cluster = df.groupby('cluster_id')['iwi'].mean().reset_index()

    # Merge the mean IWI DataFrame back with the original DataFrame to keep the other columns
    result_df = pd.merge(df, mean_iwi_per_cluster, on='cluster_id', suffixes=('', '_mean'))

    # Drop the iwi column
    result_df.drop(columns=['iwi', 'HHID'], inplace=True)
    result_df.drop_duplicates(subset=['cluster_id'], inplace=True)
    result_df.rename(columns={'iwi_mean': 'iwi'}, inplace=True)

    return result_df


def get_IWI_global(df, input_path):
    df_iwi = read_IWI(input_path, os.path.join(os.path.dirname(input_path), 'iwi.csv'))

    df_iwi = df_iwi[['HHID', 'iwi']]
    df_iwi['HHID'] = df_iwi['HHID'].str.strip()

    output = pd.merge(df, df_iwi, on='HHID', how='inner')
    output = calculate_mean_iwi_per_cluster(output)

    return output


def compute_correlation_petterson(petterson_path, global_data_lab_path):
    # Read the CSV files
    df_sustain_bench = pd.read_csv(petterson_path)
    df_sustain_bench.dropna(subset=['iwi'], inplace=True)
    df_global_data_lab = pd.read_csv(global_data_lab_path)

    # Merge the DataFrames on common columns (e.g., lat and lon)
    merged_df = pd.merge(df_sustain_bench, df_global_data_lab, on=['lat', 'lon'], suffixes=('_petterson', '_global'))
    merged_df.drop(columns=['country_global', 'year_global', 'area_of_interest', 'urban_rural', 'lat', 'lon'],
                   inplace=True)

    merged_df.to_csv('../data/merged_petterson.csv', index=False)

    # Compute the correlation between the iwi columns
    correlation = merged_df['iwi_petterson'].corr(merged_df['iwi_global'])

    return correlation


def compute_correlation_sustain(sustain_bench_path, global_data_lab_path):
    # Read the CSV files
    df_sustain_bench = pd.read_csv(sustain_bench_path)
    df_sustain_bench.dropna(subset=['iwi'], inplace=True)
    df_global_data_lab = pd.read_csv(global_data_lab_path)

    # Merge the DataFrames on common columns (e.g., country, year, cluster_id)
    merged_df = pd.merge(df_sustain_bench, df_global_data_lab, on=['country', 'year', 'cluster_id'],
                         suffixes=('_sustain', '_global'))

    # Compute the correlation between the iwi columns
    correlation = merged_df['iwi_sustain'].corr(merged_df['iwi_global'])

    return correlation


def normalize_iwi(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Normalize the 'iwi' column
    df['iwi'] = (df['iwi'] - df['iwi'].mean()) / df['iwi'].std()

    # Save the modified DataFrame back to the CSV file
    df.to_csv('../data/global_data_lab_normalized.csv', index=False)


def get_all_aoi(buffer):
    df_global = pd.read_csv('data/global_data_lab_only.csv')
    df_global['lat'] = df_global['lat'].round(6)
    df_global['lon'] = df_global['lon'].round(6)
    df_global['urban_rural'] = df_global['urban_rural'].map({1: 'U', 2: 'R'})

    df_petterson = read_petterson()
    df_sustain = read_sustain_bench()

    df_all = pd.concat([df_global, df_petterson, df_sustain], ignore_index=True)

    df_all.drop_duplicates(['lat', 'lon'], inplace=True)
    df_all.drop(['iwi'], axis=1, inplace=True)

    df_all['area_of_interest'] = df_all.apply(lambda x: area_of_interest(x['lat'],
                                                                         x['lon'],
                                                                         buffer),
                                              axis=1)

    df_all['country'] = df_all['country'].str.lower()

    df_all.sort_values(['country', 'year'], inplace=True)

    cluster_id = 0
    for i in range(len(df_all)):
        if isnan(df_all['cluster_id'].values[i]):
            df_all['cluster_id'].iloc[i] = cluster_id
            cluster_id += 1
        else:
            cluster_id = 0

    df_all['cluster_id'] = df_all['cluster_id'].astype(int)

    df_all.to_csv('data/areas_of_interest.csv', index=False, sep=';')


if __name__ == "__main__":
    sustain_path = '../data/sustain_bench.csv'
    global_data_lab_path = '../data/global_data_lab_only.csv'
    correlation_value = compute_correlation_sustain(sustain_path, global_data_lab_path)
    print(f"Correlation value: {correlation_value}")
