import argparse

from src.utils import tif_to_rgb

# once you've downloaded all the Landsat satellite images for each

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', dest='input_dir', action='store', type=str,
                    help='path to directory holding Landsat tif images')
parser.add_argument('--output_dir', dest='output_dir', action='store', type=str,
                    help='path to directory for saving Landsat jpeg images')

args = parser.parse_args()
input_dir = args.input_dir
output_dir = args.output_dir

tif_to_rgb(input_dir, output_dir)
print(f'successfully converted all input tif images, check {output_dir} for results')
