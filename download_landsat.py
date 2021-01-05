import argparse

from src.city import City
from src.satellite import Landsat

parser = argparse.ArgumentParser()
parser.add_argument('--city_name', dest='city_name', action='store',
                    help='name of city')
parser.add_argument('--data_path', dest='data_path', action='store',
                    help='absolute path to metadata.csv')
parser.add_argument('--start_date', dest='start_date', action='store',
                    help='start date for filtering ee.ImageCollection by date range')
parser.add_argument('--end_date', dest='end_date', action='store',
                    help='end date for filtering ee.ImageCollection by date range')

args = parser.parse_args()

city = City(args.city_name, args.data_path)
downloader = Landsat(city, args.start_date, args.end_date)
downloader.export_image()
