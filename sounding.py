from datetime import datetime

import numpy as np

from siphon.simplewebservice.iastate import IAStateUpperAir

def requestiowa(date, station):
    return IAStateUpperAir.request_data(date, station)

def getsounding(date, station):
    df = requestiowa(date, station)
    df_munged = df.replace({np.nan: None})
    metadata = df_munged.iloc[0][['station', 'time']]
    df_ret = df_munged[['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed', 'u_wind', 'v_wind']]
    return metadata, df_ret