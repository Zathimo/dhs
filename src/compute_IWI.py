constant = 25.00447
toilet_quality = {'low': [23, 42, 43, 96, 31], 'medium': [20, 21, 22, 41, 51], 'high': [11, 12, 13, 14, 15, 16]}
water_quality = {'low': [30, 32, 40, 42, 43, 96], 'medium': [13, 21, 31, 41, 51, 61, 62, 65, 72, 73],
                 'high': [11, 12, 14, 15, 71]}
floor_quality = {'low': [11, 12, 13, 14, 15, 16], 'medium': [20, 21, 22, 41, 51], 'high': [23, 42, 43, 96, 31]}
asset_weights = {'television': 8.612657,
                 'refrigerator': 8.429076,
                 'telephone': 7.127699,
                 'car': 4.651382,
                 'bicycle': 1.84686,
                 'cheap_utensils': 4.118394,
                 'expensive_utensils': 6.507283,
                 'electricity': 8.056664,
                 'water_quality': {'low': -6.306477, 'medium': -2.302023, 'high': 7.952443, 'missing': 0},
                 'floor_quality': {'low': -7.558471, 'medium': 1.227531, 'high': 6.107428, 'missing': 0},
                 'toilet_quality': {'low': -7.439841, 'medium': -1.090393, 'high': 8.140637, 'missing': 0},
                 'sleeping_rooms': {'one': -3.699681, 'two': 0.38405, 'three': 3.445009}}


def recode_sleeping_rooms(dataframe):
    dataframe['sleeping_rooms'] = dataframe['sleeping_rooms'].apply(
        lambda x: 'one' if x <= 1 else ('two' if x == 2 else 'three')
    )


def recode_water_quality(dataframe):
    dataframe['water_quality'] = dataframe['water_quality'].apply(
        lambda x: 'low' if x in water_quality['low']
        else ('medium' if x in water_quality['medium'] else ('high' if x in water_quality['high'] else 'missing')),
    )


def recode_toilet_quality(dataframe):
    dataframe['toilet_quality'] = dataframe['toilet_quality'].apply(
        lambda x: 'low' if x in toilet_quality['low']
        else ('medium' if x in toilet_quality['medium']
              else ('high' if x in toilet_quality['high'] else 'missing')),
    )


def recode_floor_quality(dataframe):
    dataframe['floor_quality'] = dataframe['floor_quality'].apply(
        lambda x: 'medium',
    )


def add_expensive_utensils(dataframe):
    # Add the expensive_utensils column
    dataframe['expensive_utensils'] = dataframe.apply(
        lambda row: 1 if row['car'] == 1 or row['motorboat'] == 1 or row['computer'] == 1 or row[
            'motorcycle'] == 1 else 0,
        axis=1
    )


def add_cheap_utensils(dataframe):
    # Add the cheap_utensils column
    dataframe['cheap_utensils'] = dataframe.apply(
        lambda row: 1 if row['expensive_utensils'] == 1 or row['television'] == 1 or row['refrigerator'] == 1 or
                         row['telephone'] == 1 or row['radio'] == 1 or row['bicycle'] == 1 or row['watch'] == 1 or
                         row['mobile_phone'] == 1 or row['floor_quality'] == 'high' or row[
                             'toilet_quality'] == 'high' else 0,
        axis=1
    )
    return dataframe


def add_iwi(dataframe):
    recode_toilet_quality(dataframe)
    recode_water_quality(dataframe)
    recode_sleeping_rooms(dataframe)
    recode_floor_quality(dataframe)

    add_expensive_utensils(dataframe)
    add_cheap_utensils(dataframe)

    # Add the IWI column
    dataframe['IWI'] = dataframe.apply(
        lambda row: constant
                    + asset_weights['television'] * row['television']
                    + asset_weights['refrigerator'] * row['refrigerator']
                    + asset_weights['telephone'] * row['telephone']
                    + asset_weights['car'] * row['car']
                    + asset_weights['bicycle'] * row['bicycle']
                    + asset_weights['cheap_utensils'] * row['cheap_utensils']
                    + asset_weights['expensive_utensils'] * row['expensive_utensils']
                    + asset_weights['electricity'] * row['electricity']
                    + asset_weights['water_quality'][row['water_quality']]
                    + asset_weights['floor_quality'][row['floor_quality']]
                    + asset_weights['toilet_quality'][row['toilet_quality']]
                    + asset_weights['sleeping_rooms'][row['sleeping_rooms']],
        axis=1
    )

    dataframe = dataframe[['television', 'refrigerator', 'telephone', 'bicycle', 'car', 'cheap_utensils',
                           'expensive_utensils', 'electricity', 'water_quality', 'toilet_quality', 'floor_quality',
                           'sleeping_rooms', 'IWI']]

    dataframe.to_csv('data.csv')
