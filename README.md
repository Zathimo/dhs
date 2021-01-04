Welcome to the **landsat-city** project. This is a `python3.6` and `Conda` project.

Here are some tips to get up and running.

```
# Clone the repository
git clone https://github.com/yannforget/builtup-classification-osm.git
cd landsat-city
make install
```

Downloading landsat satellite images for a city.

```
source activate landsat-city
python download_landsat.py --city_name="kampala" --data_path="/Users/JoeBloggs/workspace/landsat-city/data/" --start_date="2020-01-01" --end_date="2020-05-01"
```
