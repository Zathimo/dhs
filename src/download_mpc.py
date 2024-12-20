import pandas as pd
import rasterio
from tqdm import tqdm

import os

import test_mosaic

import logging
import hydra
from omegaconf import DictConfig, OmegaConf

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="", config_name="config")
def main(cfg: DictConfig):
    csv = pd.read_csv('data/areas_of_interest_month.csv', sep=';')

    df = convert_bbox_to_tuple(csv)
    error_log = []
    df_items = []

    for country in df['country'].unique():
        df_country = df[df['country'] == country]
        print('country:', country)
        for year in df_country['year'].unique():
            df_items_year = []
            df_year = df_country[df_country['year'] == year]
            output_path = os.path.join(os.getcwd(), "data", country, str(year))
            print('year:', year)
            if not os.path.exists(output_path):
                print(f'creating {output_path}')
                os.makedirs(output_path)

            for cluster in df_year['cluster_id'].unique():
                bbox = df_year[df_year['cluster_id'] == cluster]['area_of_interest'].values[0]
                month = df_year[df_year['cluster_id'] == cluster]['month'].values[0]
                print('cluster:', cluster, 'bbox:', bbox)

                try:
                    items = test_mosaic.cloudless_mosaic(cluster, bbox, year, month, output_path, cfg.cloud_cover,
                                                         cfg.time_span, cfg.epsg)
                    df_items_year.append({'country': country, 'year': year, 'cluster_id': cluster, "items": len(items)})
                    df_items.append(df_items_year)
                    log.info(f'Processed {country}/{year}/{cluster} with items \n {items[:]}')
                except Exception as e:
                    print(e)
                    error_log.append({'country': country, 'year': year, 'cluster_id': cluster, 'error': str(e)})
                    log.error(f'Error processing {country}/{year}/{cluster}: {e}')

            df_items_year = pd.DataFrame(df_items_year)
            df_items_year.to_csv(f'data/{country}/{year}/items_per_cluster_1y_cloud25.csv', index=False, sep=';')

    df_items_year = pd.DataFrame(df_items)
    df_items_year.to_csv(f'data/items_per_cluster_1y_cloud25.csv', index=False, sep=';')

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


def select_landsat7(dataset_csv, data_path, output_path):
    data = []

    dataframe = pd.read_csv(dataset_csv, sep=';')

    for idx in tqdm(range(len(dataframe))):

        row = dataframe.iloc[idx]

        tile_name = os.path.join(data_path,
                                 str(row.country),
                                 str(row.year),
                                 str(row.cluster) + ".tif"
                                 )

        with rasterio.open(tile_name) as src:
            if len(src.indexes) == 19:
                data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False, sep=';')


def dataset_random_split(dataset_csv, output_path, train_ratio=0.8):
    df = pd.read_csv(dataset_csv, sep=';')

    train_df = df.sample(frac=train_ratio)
    test_df = df.drop(train_df.index)

    train_df.to_csv(output_path + '/train.csv', index=False, sep=';')
    test_df.to_csv(output_path + '/test.csv', index=False, sep=';')


if __name__ == "__main__":
    main()