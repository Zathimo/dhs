Welcome to the **landsat-city** project. This is a `python3` and `Conda` project.

# Getting started

You'll need a Google Earth Engine account.

Here are some tips to get up and running.

```
# Clone the repository
git clone git@github.com:p4tr1ckc4rs0n/landsat-city.git
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

# Motivation

Having time a series of regular and consistent observations of built settlement extents is important given that forecasted growth of populations within dense urban areas are expected to continue through 2050, with much of that increase will occur within Africa and Asia (Angel, Sheppard, & Civco, 2005; United Nations, 2015b). Rapidly changing magnitudes and distributions of both built-settlements and populations have significant implications for sustainability (Cohen, 2006), climate change (McGranahan, Balk, & Anderson, 2007; Stephenson, Newman, & Mayhew, 2010), and public health (Chongsuvivatwong et al., 2011; Dhingra et al., 2016). 

The 2030 Agenda for Sustainable Development, which have a focus on accounting for and including “all people everywhere”, reinforced the need for readily and globally available baseline data to guide efforts and measure progress toward its Sustainable Development Goals (SDGs) (United Nations, 2016).

Code heavily inspired by:
1. https://github.com/yannforget/builtup-classification-osm/
2. https://github.com/sustainlab-group/africa_poverty
