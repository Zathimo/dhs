Welcome to the **landsat-city** project. This is a `python3` and `Conda` project.

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
source deacivate landsat-city
```

Downloading landsat 8 satellite image for a city.

```
source activate landsat-city

cd landsat-city

python download_landsat.py --city_name="kampala" --data_path="/Users/JoeBloggs/workspace/landsat-city/data/" --start_date="2020-01-01" --end_date="2020-05-01"
```

Code heavily inspired by:
1. https://github.com/yannforget/builtup-classification-osm/
2. https://github.com/sustainlab-group/africa_poverty
