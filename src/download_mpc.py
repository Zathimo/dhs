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


if __name__ == "__main__":
    main()
