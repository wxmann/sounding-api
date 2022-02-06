from functools import lru_cache

import numpy as np
import pandas as pd
from siphon.simplewebservice.wyoming import WyomingUpperAir

_DATA_FIELDS = [
    'pressure', 'height', 'temperature', 'dewpoint',
    'wind_dir', 'wind_speed'
]

_META_FIELDS = [
    'latitude', 'longitude', 'elevation',
    'station', 'station_number'
]


def get_sounding(ts, site):
    df = get_sounding_df(ts, site)
    metadata = df.iloc[0][_META_FIELDS]
    metadata_dict = metadata.to_dict()
    data_dict = {
        'profile': df[_DATA_FIELDS].to_dict('records')
    }
    return metadata_dict | data_dict


@lru_cache()
def get_sounding_df(ts, site):
    requester = WyomingUpperAir()
    df = requester.request_data(time=pd.Timestamp(ts), site_id=site)

    return df.rename(columns={
        'direction': 'wind_dir',
        'speed': 'wind_speed'
    }).replace({
        np.nan: None,
        np.inf: None
    })