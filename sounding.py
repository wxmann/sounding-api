from functools import lru_cache

import numpy as np
import pandas as pd
from siphon.simplewebservice.wyoming import WyomingUpperAir

_DATA_FIELDS = [
    'pressure', 'height', 'temperature', 'dewpoint',
    'direction', 'speed', 'u_wind', 'v_wind'
]

_META_FIELDS = [
    'latitude', 'longitude', 'elevation',
    'station', 'station_number'
]


def to_dict(sounding_df):
    metadata = sounding_df.iloc[0][_META_FIELDS]
    metadata_dict = metadata.to_dict()
    data_dict = {
        'profile': sounding_df[_DATA_FIELDS].to_dict('records')
    }
    return metadata_dict | data_dict


@lru_cache()
def get_sounding(ts, site, fill_value=None):
    requester = WyomingUpperAir()
    df = requester.request_data(time=pd.Timestamp(ts), site_id=site)

    return df.replace({
        np.nan: fill_value,
        np.inf: fill_value
    })