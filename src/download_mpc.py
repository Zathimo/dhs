import pandas as pd

import os

import test_mosaic

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


def main():
    csv = pd.read_csv('data/areas_of_interest.csv', sep=';')

    df = convert_bbox_to_tuple(csv)
    error_log = []

    for country in df['country'].unique():
        df_country = df[df['country'] == country]
        for year in df_country['year'].unique():
            df_year = df_country[df_country['year'] == year]
            output_path = os.path.join(os.getcwd(), "data", country, str(year))
            if not os.path.exists(output_path):
                print(f'creating {output_path}')
                os.makedirs(output_path)

            for cluster in df_year['cluster_id'].unique():
                bbox = df_year[df_year['cluster_id'] == cluster]['area_of_interest'].values[0]
                print('cluster:', cluster, 'bbox:', bbox)

                try:
                    test_mosaic.cloudless_mosaic(cluster, bbox, year, output_path)
                except Exception as e:
                    error_log.append({'country': country, 'year': year, 'cluster_id': cluster, 'error': str(e)})

    if error_log:
        error_df = pd.DataFrame(error_log)
        error_df.to_csv('data/errors.csv', index=False, sep=';')


def convert_bbox_to_tuple(df):
    # Convert the area_of_interest column to tuple of floats
    df['area_of_interest'] = df['area_of_interest'].apply(lambda x: tuple(map(float, x.strip('[]').split(','))))

    return df


def extract_country_year_cluster(data_path, output_path):
    data = []

    for country_folder in os.listdir(data_path):
        country_path = os.path.join(data_path, country_folder)
        if os.path.isdir(country_path):
            for year_folder in os.listdir(country_path):
                year_path = os.path.join(country_path, year_folder)
                if os.path.isdir(year_path):
                    for cluster_file in os.listdir(year_path):
                        if cluster_file.endswith('.tif'):
                            cluster_id = int(cluster_file.split('.')[0])
                            data.append({'country': country_folder, 'year': year_folder, 'cluster_id': cluster_id})

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False, sep=';')


if __name__ == "__main__":
    aoi = pd.read_csv('../data/global_data_lab_only.csv', sep=',')
    aoi['country'] = aoi['country'].apply(lambda x: x.lower())
    cyc = pd.read_csv('data/downloaded_aoi.csv', sep=';')
    filtered = pd.merge(cyc, aoi, on=['country', 'year', 'cluster_id'])
    filtered.to_csv('data/filtered_dataset.csv', index=False, sep=';')
