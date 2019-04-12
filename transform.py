import numpy as np


def dictify_ser(ser):
    ret = ser.to_dict()
    return _fix_jsonification(ret)


def dictify_df(df):
    ret = df.to_dict('records')

    if isinstance(ret, list):
        return [_fix_jsonification(thing) for thing in ret]

    return _fix_jsonification(ret)


def _fix_jsonification(thing):
    for key, value in thing.items():
        if hasattr(value, 'isoformat'):
            thing[key] = value.isoformat()
        if isinstance(value, (np.int64)):
            thing[key] = int(value)
    return thing