import pandas as pd

import matplotlib.pyplot as plt
import scipy.stats
import pyreadstat

import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


def read_IWI(input_path, output_path):
    df, meta = pyreadstat.read_sav(input_path)

    df.to_csv(output_path, index=False)
    output = pd.read_csv(output_path, sep=',')

    return output


def get_IWI_petterson(df):
    df = df.drop_duplicates('cluster_id')
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


if __name__ == "__main__":
    pass
