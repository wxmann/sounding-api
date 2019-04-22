from functools import lru_cache

import numpy as np

from siphon.simplewebservice.iastate import IAStateUpperAir
from siphon.simplewebservice.wyoming import WyomingUpperAir

_PRIMARY_CONUS_STATIONS = {
    'UIL', 'SLE', 'MFR', 'OTX', 'BOI',  # WA/OR/ID
    'OAK', 'VBG', 'NKX', 'EDW',   # CA
    'REV', 'VEF', 'LKN', 'SLC'    # NV, Great Basin
    'TFW', 'GGW', 'RIW',   # MT/WY
    'FGW', 'TUS', 'ABQ', 'GJT', 'DNR',  # AZ/CO/NM
    'BIS', 'ABR', 'UNR', 'LBF', 'OAX',  # Northern Plains (ND/SD/NE)
    'DDC', 'TOP', 'OUN',  # Central/South Plains (OK/KS)
    'AMA', 'MAF', 'EPZ', 'DRT', 'FWD', 'CRP', 'BRO',   # TX
    'INL', 'MPX', 'GRB', 'DVN',   # MN/WI/IA
    'SGF', 'LZK', 'SHV', 'LCH', 'SIL',  # MO/AR/LA
    'ILX', 'ILN', 'APX', 'DTX',   # upper midwest (IL/IN/MI/OH)
    'JAN', 'BMX', 'BNA', 'FFC',   # dixie (MS/AL/GA/TN)
    'BUF', 'PIT', 'ALB', 'OKX',   # NY/PA/NJ
    'GYX', 'CAR', 'CHH',   # New England
    'IAD', 'WAL', 'RNK',   # Mid-Atlantic
    'GSO', 'MHX', 'CHS',   # Carolinas
    'TLH', 'JAX', 'XMR', 'TBW', 'MFL', 'EYW'  # FL
}

def requestiowa(date, station):
    return IAStateUpperAir.request_data(date, station)


def requestwyoming(date, station):
    return WyomingUpperAir.request_data(date, station)


@lru_cache()
def getsounding(date, station):
    station = station.upper()
    if station in _PRIMARY_CONUS_STATIONS:
        df = requestiowa(date, station)
    else:
        df = requestwyoming(date, station)

    df_munged = df.replace({np.nan: None})
    metadata = df_munged.iloc[0][['station', 'time']]
    df_ret = df_munged[['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed', 'u_wind', 'v_wind']]
    return metadata, df_ret