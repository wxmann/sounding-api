from datetime import datetime

import pandas as pd

from sounding import getsounding
from thermo import sbparcel, extract_env_profile, mlparcel
from transform import dictify_ser, dictify_df


def sounding_handler(year, month, day, hour, station):
    ts = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour))
    info, data = getsounding(ts, station)
    response_body = {
        'info': dictify_ser(info),
        'data': dictify_df(data)
    }
    return response_body


def parameter_handler(soundingdata):
    soundingdata = soundingdata['data']
    df = pd.DataFrame(soundingdata)
    p, T, Td = extract_env_profile(df)
    sb = _parcel_info(sbparcel(p, T, Td))
    ml = _parcel_info(mlparcel(p, T, Td))
    return {
        'sb_parcel': sb,
        'ml_parcel': ml
    }


def _parcel_info(parcel):
    lclp, _ = parcel.lcl()
    lfcp, _ = parcel.lfc()
    lfcvtp, _ = parcel.lfc_vt()
    elp, _ = parcel.el()
    elvtp, _ = parcel.el_vt()

    profilep, profileT = parcel.profile()
    profilevtp, profilevtT = parcel.profile_vt()

    non_corrected = {
        'profile': _parcel_dict(profilep.magnitude, profileT.magnitude),
        'cape': parcel.cape().magnitude,
        'cin': parcel.cin().magnitude,
        'lcl': lclp.magnitude,
        'lfc': lfcp.magnitude,
        'el': elp.magnitude
    }

    virtual_corrected = {
        'profile': _parcel_dict(profilevtp.magnitude, profilevtT.magnitude),
        'cape': parcel.cape_vt().magnitude,
        'cin': parcel.cin_vt().magnitude,
        'lcl': lclp.magnitude,
        'lfc': lfcvtp.magnitude,
        'el': elvtp.magnitude
    }

    return {
        'non_corrected': non_corrected,
        'virtual_temp_corrected': virtual_corrected
    }

def _parcel_dict(p, T):
    return [{
        'pressure': pval,
        'temperature': Tval
    } for pval, Tval in zip(p, T)]