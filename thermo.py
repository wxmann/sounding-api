from collections import namedtuple

# this monkey patch fixes the LFC calculation
from monkey_patch import *

import metpy.calc as mpcalc
from metpy.units import units
import numpy as np

Quantity = units.Quantity

Ob = namedtuple('Ob', ['p', 'T'])


def sbparcel(p, T, Td):
    p0, T0, Td0 = p[0], T[0], Td[0]
    return Parcel(p, T, Td, p0, T0, Td0)


def mlparcel(p, T, Td):
    pml, Tml, Tdml = mpcalc.mixed_parcel(p, T, Td)
    return Parcel(p, T, Td, pml, Tml, Tdml)


def virtualtemp(p, T, Td):
    r = mpcalc.saturation_mixing_ratio(p, Td)
    vt_raw = mpcalc.virtual_temperature(T, r).to('kelvin')
    Tk = T.to('kelvin')
    p_hpa = p.to('hPa')

    # in a perfect world we're done here, but in many raobs the dewpoint data at higher altitudes
    # is missing. Fortunately the virtual temperature correction is on order of ~0.2 K or less
    # for low mixing ratios at high altitudes.
    vt_corrected = np.where((np.isnan(vt_raw.magnitude) & (p_hpa.magnitude < 500)), Tk, vt_raw)
    return Quantity(vt_corrected, 'kelvin')


class Parcel(object):
    def __init__(self,
                 environ_p, environ_T, environ_Td,
                 parcel_p0, parcel_T0, parcel_Td0):

        p2 = environ_p.copy()
        T2 = environ_T.copy()
        Td2 = environ_Td.copy()
        p2[0] = parcel_p0
        T2[0] = parcel_T0
        Td2[0] = parcel_Td0

        self._parcelp, Twithlcl, Tdwithlcl, self._parcelT = mpcalc.parcel_profile_with_lcl(p2, T2, Td2)
        self._lclp, self._lclT = mpcalc.lcl(parcel_p0, parcel_T0, parcel_Td0)

        # buoyancy quantities, no virtual temperature correction
        self._cape, self._cin = mpcalc.cape_cin(self._parcelp, Twithlcl, Tdwithlcl, self._parcelT)
        self._lfcp, self._lfcT = mpcalc.lfc(self._parcelp, Twithlcl, Tdwithlcl, self._parcelT)
        self._elp, self._elT = mpcalc.el(self._parcelp, Twithlcl, Tdwithlcl, self._parcelT)

        # virtual temperature correction
        self._parcelp_vt, self._parcelT_vt = self._parcel_vt_correct()
        Tvirt = virtualtemp(self._parcelp, Twithlcl, Tdwithlcl)

        self._cape_vt, self._cin_vt = mpcalc.cape_cin(self._parcelp, Tvirt, Tdwithlcl, self._parcelT_vt)
        self._lfcp_vt, self._lfcT_vt = mpcalc.lfc(self._parcelp, Tvirt, Tdwithlcl, self._parcelT_vt)
        self._elp_vt, self._elT_vt = mpcalc.el(self._parcelp, Tvirt, Tdwithlcl, self._parcelT_vt)


    def _parcel_vt_correct(self):
        parcelp_Tv = self._parcelp

        # Below the LCL, the parcel is lifted with a constant mixing ratio (that which reaches
        # saturation at the LCL). Above the LCL, the parcel is saturated so the
        # mixing ratio = the saturation mixing ratio at each parcel ascent point.
        r_lcl = mpcalc.saturation_mixing_ratio(self._lclp, self._lclT)
        corrected_below_lcl = mpcalc.virtual_temperature(self._parcelT, r_lcl).to('kelvin')
        corrected_above_lcl = mpcalc.virtual_temperature(
            self._parcelT,
            mpcalc.saturation_mixing_ratio(self._parcelp, self._parcelT)).to('kelvin')

        parcel_tv_corrected = np.where(parcelp_Tv >= self._lclp, corrected_below_lcl, corrected_above_lcl)
        return parcelp_Tv, Quantity(parcel_tv_corrected, 'kelvin')


    def profile(self, pres_unit='hPa', temp_unit='degC'):
        return Ob(p=self._parcelp.to(pres_unit), T=self._parcelT.to(temp_unit))

    def lcl(self, pres_unit='hPa', temp_unit='degC'):
        return Ob(p=self._lclp.to(pres_unit), T=self._lclT.to(temp_unit))

    def lfc(self, pres_unit='hPa', temp_unit='degC'):
        return Ob(p=self._lfcp.to(pres_unit), T=self._lfcT.to(temp_unit))

    def el(self, pres_unit='hPa', temp_unit='degC'):
        return Ob(p=self._elp.to(pres_unit), T=self._elT.to(temp_unit))

    def cape(self):
        return self._cape

    def cin(self):
        return self._cin

    def lfc_vt(self, pres_unit='hPa', temp_unit='degC'):
        return Ob(p=self._lfcp_vt.to(pres_unit), T=self._lfcT_vt.to(temp_unit))

    def el_vt(self, pres_unit='hPa', temp_unit='degC'):
        return Ob(p=self._elp_vt.to(pres_unit), T=self._elT_vt.to(temp_unit))

    def cape_vt(self):
        return self._cape_vt

    def cin_vt(self):
        return self._cin_vt
