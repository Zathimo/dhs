Welcome to the **dhs-landsat-download** project. This is a `python3` and `Conda` project.

# Getting started

You'll need a Google Earth Engine account.

Here are some tips to get up and running.

```
# Clone the repository
git clone https://github.com/p4tr1ckc4rs0n/landsat-city.git
cd dhs-landsat-download

# Create the Python environment
conda env create --file osx_environment.yml

# Activate the environment
source activate dhs-landsat-download

# Deacivate the environment
source deactivate dhs-landsat-download
```

# Process DHS data

Demographic and Health Surveys (DHS) are nationally-representative household surveys that provide data for a wide range of monitoring and impact evaluation indicators in the areas of population, health, and nutrition. Access to the survey data requires registration [DHS Survey Dataset sign up](https://dhsprogram.com/data/dataset_admin/login_main.cfm?CFID=17027270&CFTOKEN=c4c188f84eaedb52-487F1EA8-E5D7-6CFA-5B97BD18ADC2BD5E).

```
cd  


```

# Download associated landsat images for each cluster. Save to Google Drive

Downloading landsat 8 satellite image for a city to your Google Drive.

```
source activate dhs-landsat-download

cd dhs-landsat-download

download_landsat.py --country="burindi" --country_cluster="/Path/to/burindi_cluster_wealth.csv" --start_date="2016-01-01" --end_date="2017-12-31"

```

# Working with Output

Download the image.tif file from your Google Drive, load and view it with `rasterio`.

```
import rasterio as rio
from rasterio.plot import show
import matplotlib.pylab as plt

city_scene = rio.open('/path/to/image.tif')

fig, ax = plt.subplots(1, figsize=(18,18))
show(city_scene.read(1))
plt.show()
```

# Motivation

Having time a series of regular and consistent observations of built settlement extents is important given that forecasted growth of populations within dense urban areas are expected to continue through 2050, with much of that increase will occur within Africa and Asia. Rapidly changing magnitudes and distributions of both built-settlements and populations have significant implications for sustainability, climate change, and public health. 

The 2030 Agenda for Sustainable Development, which have a focus on accounting for and including “all people everywhere”, reinforced the need for readily and globally available baseline data to guide efforts and measure progress toward its Sustainable Development Goals (SDGs).

Code heavily inspired by:
1. https://github.com/yannforget/builtup-classification-osm/
2. https://github.com/sustainlab-group/africa_poverty
