Welcome to the **dhs-landsat-download** project. This is a `python3` and `Conda` project.

# Idea

Demographic and Health Surveys (DHS) are nationally-representative household surveys that provide data for a wide range of monitoring and impact evaluation indicators in the areas of population, health, and nutrition. What if we could pair freely available landsat 8 satellite images with this data?

# Getting started

You'll need a [Demographic and Health Surveys (DHS)](https://dhsprogram.com/data/dataset_admin/login_main.cfm?CFID=17027270&CFTOKEN=c4c188f84eaedb52-487F1EA8-E5D7-6CFA-5B97BD18ADC2BD5E) account to download the DHS survey data and a [Google Earth Engine](https://signup.earthengine.google.com/#!/) account to download and store the satellite images.

Here are some tips to get up and running.

```
# Clone the repository
git clone https://github.com/p4tr1ckc4rs0n/dhs-landsat-dowbload.git
cd dhs-landsat-download

# Create the Python environment
conda env create --file osx_environment.yml

# Activate the environment
source activate dhs-landsat
```

# Process DHS data

Download the the DHS survey data, don't forget to request the GPS dataset too. Run the `process_dhs.py` script to extract the wealth index for each cluster and generate a 10x10km bounding box around each cluster latitiude and longitude.

```
python process_dhs.py --country="burindi" --dhs_survey="/Path/to/BUHR71FL.DTA" --dhs_gps="/Path/to/BUGE71FL.shp
```

Running this script should yield a `burindi_cluster_wealth.csv` file with the mean wealth index for each cluster and associated bounding box.

# Download associated landsat images for each cluster. Save to Google Drive

Downloading landsat 8 satellite images for each cluster.  Run the `download_landsat.py` scipt to download 10x10km daylight and nightlight images for each cluster in the DHS survey. This may take a long time depending on how many clusters exist in the survey. Make sure the `start_date` and `end_date` match the years in which the DHS survey was conducted.

```
python download_landsat.py --country="burindi" --country_cluster="/Path/to/burindi_cluster_wealth.csv" --start_date="2016-01-01" --end_date="2017-12-31"
```

Once this script is done running you should end up with 100s, sometimes 1000s of satellite images, for each cluster saved in you goodle drive under`/<country>` the file name pertains to the country, start and end date of the satellite image composite and cluster id: `<country>_<start_date>_<end_date>_<cluster_id>.tif`.

# Working with the satellite image output

Download the image.tif file from your Google Drive, load and view it with `rasterio`.

```
import rasterio as rio
from rasterio.plot import show
import matplotlib.pylab as plt

scene = rio.open('/path/to/image.tif')

fig, ax = plt.subplots(1, figsize=(18,18))
show(scene.read(1))
plt.show()
```

# Motivation

The 2030 Agenda for Sustainable Development, which have a focus on accounting for and including “all people everywhere”, reinforced the need for readily and globally available baseline data to guide efforts and measure progress toward its Sustainable Development Goals (SDGs).

Code heavily inspired by:
1. https://github.com/yannforget/builtup-classification-osm/
2. https://github.com/sustainlab-group/africa_poverty
