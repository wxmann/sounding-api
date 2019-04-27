from functools import wraps

import metpy
import metpy.calc as mpcalc
from packaging import version

if version.parse(metpy.__version__) <= version.parse('0.10.0'):
    original_lfc_func = mpcalc.lfc

    @wraps(original_lfc_func)
    def patched_lfc_func(pressure, temperature, dewpt, parcel_temperature_profile=None):
        try:
            return original_lfc_func(pressure, temperature, dewpt, parcel_temperature_profile)
        except IndexError:
            # An IndexError would occur if the intersection of the temperature and parcel
            # curves occured beneath the LCL. This was fixed in
            # https://github.com/Unidata/MetPy/pull/1022, and it is applied here as a
            # monkey-patch.
            x, y = mpcalc.lcl(pressure[0], temperature[0], dewpt[0])
            return x, y

    # referenced by direct invocation of metpy.calc API
    mpcalc.lfc = patched_lfc_func

    # referenced within CAPE calculation of metpy.calc
    mpcalc.thermo.lfc = patched_lfc_func