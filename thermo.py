from collections import namedtuple

import metpy.calc as mpcalc

Ob = namedtuple('Ob', ['p', 'T'])


def sbparcel(p, T, Td):
    p0, T0, Td0 = p[0], T[0], Td[0]
    return ParcelThermoCalculator(p, T, Td, p0, T0, Td0)


def mlparcel(p, T, Td):
    pml, Tml, Tdml = mpcalc.mixed_parcel(p, T, Td)
    return ParcelThermoCalculator(p, T, Td, pml, Tml, Tdml)


class ParcelThermoCalculator(object):
    def __init__(self,
                 environ_p, environ_T, environ_Td,
                 parcel_p0, parcel_T0, parcel_Td0):

        p2 = environ_p.copy()
        T2 = environ_T.copy()
        Td2 = environ_Td.copy()
        p2[0] = parcel_p0
        T2[0] = parcel_T0
        Td2[0] = parcel_Td0

        self._parcelp, newT, newTd, self._parcelT = mpcalc.parcel_profile_with_lcl(p2, T2, Td2)
        self._lclp, self._lclT = mpcalc.lcl(parcel_p0, parcel_T0, parcel_Td0)
        self._cape, self._cin = mpcalc.cape_cin(self._parcelp, newT, newTd, self._parcelT)
        self._lfcp, self._lfcT = mpcalc.lfc(self._parcelp, newT, newTd, self._parcelT)
        self._elp, self._elT = mpcalc.el(self._parcelp, newT, newTd, self._parcelT)

    def parcel_profile(self, pres_unit='hPa', temp_unit='degC'):
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
