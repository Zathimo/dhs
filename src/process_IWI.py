import pandas as pd

import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import scipy.stats

import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

def read_IWI():
    import pyreadstat

    df, meta = pyreadstat.read_sav('../data/Angola2011-addIWI.sav')

    print(df['HHID'][1])

    # done! let's see what we got
    print(df.head())
    print(meta.column_names)
    print(meta.column_labels)
    print(meta.column_names_to_labels)
    print(meta.number_rows)
    print(meta.number_columns)
    print(meta.file_label)
    print(meta.file_encoding)
    # there are other metadata pieces extracted. See the documentation for more details.

    df.to_csv('../data/Angola2011-addIWI.csv')


def read_sustain_bench():
    df = pd.read_csv('../data/dhs_final_labels.csv')[['cname', 'year', 'cluster_id', 'lat', 'lon', 'asset_index']]
    df = df[df['cname'] == 'AO'].drop(columns=['cname'])
    df = df[df['year'] == 2011].drop(columns=['year'])
    df.rename(columns={'asset_index': 'iwi_yeh'}, inplace=True)
    df.to_csv('../data/sustain_bench.csv', index=False)


def read_petterson():
    df = pd.read_csv('../data/dhs_clusters_rounded.csv')[['country', 'survey_start_year', 'lat', 'lon', 'iwi']]
    df = df[df['country'] == 'angola'].drop(columns=['country'])
    df = df[df['survey_start_year'] == 2011].drop(columns=['survey_start_year'])
    df.rename(columns={'iwi': 'iwi_petterson'}, inplace=True)
    df.to_csv('../data/petterson.csv', index=False)


def merge_all():
    sustain = pd.read_csv('../data/sustain_bench.csv')
    petterson = pd.read_csv('../data/petterson.csv')
    smits = pd.read_csv('../data/Angola/dhs/mean_iwi_per_cluster.csv')
    df = pd.merge(sustain, petterson, on=['lat', 'lon'], how='inner')
    df = pd.merge(smits, df, on=['cluster_id', 'lat', 'lon'], how='inner')
    df.to_csv('../data/merged.csv', index=False)


def round_lat_lon(csv_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Round the lat and lon columns to 6 decimal places
    df['lat'] = df['lat'].round(6)
    df['lon'] = df['lon'].round(6)

    # Save the modified DataFrame back to a CSV file
    df.to_csv(output_path, index=False)


def calculate_mean_iwi_per_cluster(csv_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path, sep=';')
    print(df.head())

    # Group by cluster_id and calculate the mean IWI
    mean_iwi_per_cluster = df.groupby('cluster_id')['iwi'].mean().reset_index()

    # Merge the mean IWI DataFrame back with the original DataFrame to keep the other columns
    result_df = pd.merge(df, mean_iwi_per_cluster, on='cluster_id', suffixes=('', '_mean'))

    # Drop the iwi column
    result_df.drop(columns=['iwi', 'HHID'], inplace=True)
    result_df.drop_duplicates(inplace=True)

    return result_df


def normalize_iwi(csv_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Convert the iwi column to integers
    df['iwi_petterson'] = df['iwi_petterson'].astype(float)

    # Initialize the MinMaxScaler
    scaler = MinMaxScaler()

    # Normalize the iwi column
    df['iwi_petterson'] = scaler.fit_transform(df[['iwi_petterson']])*100

    # Save the modified DataFrame back to a CSV file
    df.to_csv(output_path, index=False)


def compute_iwi_mean_from_iwi_petterson(csv_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Convert the iwi_petterson column to float
    df['iwi_petterson'] = df['iwi_petterson'].astype(float)
    df['iwi_mean'] = df['iwi_mean'].astype(float)

    slope, intercept, r, p, stderr = scipy.stats.linregress(df['iwi_petterson'], df['iwi_mean'])
    print('r²:', r**2)
    # Compute the correlation between iwi_petterson and iwi_mean
    correlation = df['iwi_petterson'].corr(df['iwi_mean'])

    # Print the correlation value
    print(f'Correlation between iwi_petterson and iwi_mean: {correlation}')

    # Compute the mean of the normalized iwi_petterson values
    df['iwi_petterson'] = df['iwi_petterson']*slope + intercept

    slope, intercept, r, p, stderr = scipy.stats.linregress(df['iwi_petterson'], df['iwi_mean'])
    print('r²:', r ** 2)
    # Compute the correlation between iwi_petterson and iwi_mean
    correlation = df['iwi_petterson'].corr(df['iwi_mean'])

    # Print the correlation value
    print(f'Correlation between iwi_petterson and iwi_mean: {correlation}')

    # Save the modified DataFrame back to a CSV file
    df.to_csv(output_path, index=False)

if __name__ == "__main__":

    csv_path = '../data/merged.csv'
    output_path = '../data/modified.csv'
    compute_iwi_mean_from_iwi_petterson(csv_path, output_path)

    # Read the merged CSV file into a DataFrame
    df = pd.read_csv('../data/modified.csv')

    # Compute the correlation between iwi_petterson and iwi_mean
    correlation = df['iwi_petterson'].corr(df['iwi_mean'])

    # Print the correlation value
    print(f'Correlation between iwi_petterson and iwi_mean: {correlation}')

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(df['iwi_petterson'], df['iwi_mean'])

    # Compute the R² value
    r_squared = r_value ** 2

    # Print the R² value
    print(f'R² between iwi_petterson and iwi_mean: {r_squared}')

    # Create a scatter plot of iwi_petterson versus iwi_mean
    plt.figure(figsize=(10, 6))
    plt.scatter(df['iwi_mean'], df['iwi_petterson'], color='b', label='IWI Petterson vs IWI Mean')

    # Add labels and title
    plt.xlabel('IWI Mean')
    plt.ylabel('IWI Petterson')
    plt.title('IWI Petterson vs IWI Mean')

    # Display the plot
    plt.legend()
    plt.show()

    # Create a figure
    plt.figure(figsize=(10, 6))

    # Plot iwi_petterson against cluster_id
    plt.plot(df['cluster_id'], df['iwi_petterson'], marker='o', linestyle='-', color='b', label='IWI Petterson')

    # Plot iwi_mean against cluster_id
    plt.plot(df['cluster_id'], df['iwi_mean'], marker='o', linestyle='-', color='r', label='IWI Mean')

    # Add labels and title
    plt.xlabel('Cluster ID')
    plt.ylabel('IWI')
    plt.title('IWI Petterson and IWI Mean vs Cluster ID')

    # Add legend
    plt.legend()

    # Display the plot
    plt.show()