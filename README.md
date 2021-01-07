Welcome to the **landsat-city** project. This is a `python3` and `Conda` project.

# Getting started

You'll need a Google Earth Engine account.

Here are some tips to get up and running.

```
# Clone the repository
git clone https://github.com/p4tr1ckc4rs0n/landsat-city.git
cd landsat-city

# Create the Python environment
conda env create --file osx_environment.yml

# Activate the environment
source activate landsat-city

# Deacivate the environment
source deactivate landsat-city
```

# Output

Downloading landsat 8 satellite image for a city to your Google Drive.

```
source activate landsat-city

cd landsat-city

python download_landsat.py --city_name="kampala" --data_path="/Users/JoeBloggs/workspace/landsat-city/data/" --start_date="2020-01-01" --end_date="2020-05-01"
```

# Working with Output

Download the image.tif file from your Google Drive.

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
