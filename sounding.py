from datetime import datetime

import numpy as np

from siphon.simplewebservice.wyoming import WyomingUpperAir

def requestwyoming(date, station):
    return WyomingUpperAir.request_data(date, station)

def getsounding(date, station):
    df = requestwyoming(date, station)
    df_munged = df.replace({np.nan: None})
    metadata = df_munged.iloc[0][['station', 'station_number', 'time', 'latitude', 'longitude', 'elevation']]
    df_ret = df_munged[['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed', 'u_wind', 'v_wind']]
    return metadata, df_ret