'''
datasets.py -- Routines for dataset-specfic capabilities:  file handling, readers, etc.

One Class for each dataset containing static methods and constants/templates, etc.

'''

import sys, os, re, datetime

from split import splitByNDaysKeyed, groupByKeys, extractKeys

def splitModisAod(seq, n):
    return splitByNDaysKeyed(seq, n, re.compile(r'(....)(..)(..)'), lambda y, m, d: ymd2doy(y,m,d))

def splitAvhrrSst(seq, n):
    return splitByNDays_Avhrr(seq, n, re.compile(r'^(....)(..)(..)'))


class ModisSst:
    ExpectedRunTime = "28m"
    UrlsPath = "/data/share/datasets/MODIS_L3_AQUA_11UM_V2014.0_4KM_DAILY/daily_data/A*SST*.nc"
    ExampleFileName = 'A2010303.L3m_DAY_NSST_sst_4km.nc'
    GetKeysRegex = r'A(....)(...).L3m_DAY_(.)S'

    VariableName = 'sst'
    Mask = None
    Coordinates = ['lat', 'lon']

    OutputClimTemplate = ''

    @staticmethod
    def keysTransformer(s): return (s[1], s[0], s[2])      # DOY, YEAR, N=night / S=day

    @staticmethod
    def getKeys(url):
        return extractKeys(url, ModisSst.GetKeysRegex, ModisSst.keysTransformer)

    @staticmethod
    def split(seq, n):
        return [u for u in splitByNDaysKeyed(seq, n, ModisSst.GetKeysRegex, ModisSst.keysTransformer)]

    @staticmethod
    def genOutputName(doy, variable, nEpochs, averagingConfig):
        return 'A%03d.L3m_%s_%dday_clim_%s.nc' % (doy, variable, nEpochs, averagingConfig['name'])    # mark each file with first day in period


class ModisChlor:
    ExpectedRunTime = "11m"
    UrlsPath = "/data/share/datasets/MODIS_L3m_DAY_CHL_chlor_a_4km/daily_data/A*chlor*.nc"
    ExampleFileName = "A2013187.L3m_DAY_CHL_chlor_a_4km.nc"
    GetKeysRegex = r'A(....)(...).L3m.*CHL'

    Variable = 'chlor_a'
    Mask = None
    Coordinates = ['lat', 'lon']

    OutputClimTemplate = ''

    @staticmethod
    def keysTransformer(s): return (s[1], s[0])      # DOY, YEAR

    @staticmethod
    def getKeys(url):
        return extractKeys(url, ModisChlor.GetKeysRegex, ModisChlor.keysTransformer)

    @staticmethod
    def split(seq, n):
        return [u for u in splitByNDaysKeyed(seq, n, ModisChlor.GetKeysRegex, ModisChlor.keysTransformer)]

    @staticmethod
    def genOutputName(doy, variable, nEpochs, averagingConfig):
        return 'A%03d.L3m_%s_%dday_clim_%s.nc' % (doy, variable, nEpochs, averagingConfig['name'])    # mark each file with first day in period


class MeasuresSsh:
    ExpectedRunTime = "2m22s"
    UrlsPath = "/data/share/datasets/MEASURES_SLA_JPL_1603/daily_data/ssh_grids_v1609*12.nc"
    ExampleFileName = "ssh_grids_v1609_2006120812.nc"
    GetKeysRegex = r'ssh.*v1609_(....)(..)(..)12.nc'

    Variable = 'SLA'   # sea level anomaly estimate
    Mask = None
    Coordinates = ['Longitude', 'Latitude']    # Time is first (len=1) coordinate, will be removed

    OutputClimTemplate = ''

    @staticmethod
    def keysTransformer(s): return (ymd2doy(s[0], s[1], s[2]), s[0])      # DOY, YEAR

    @staticmethod
    def getKeys(url):
        return extractKeys(url, MeasuresSsh.GetKeysRegex, MeasuresSsh.keysTransformer)

    @staticmethod
    def split(seq, n):
        return [u for u in splitByNDaysKeyed(seq, n, MeasuresSsh.GetKeysRegex, MeasuresSsh.keysTransformer)]

    @staticmethod
    def genOutputName(doy, variable, nEpochs, averagingConfig):
        return "ssh_grids_v1609_%03d_%dday_clim_%s.nc" % (int(doy), nEpochs, averagingConfig['name'])


class CCMPWind:
    ExpectedRunTime = "?"
    UrlsPath = "/data/share/datasets/CCMP_V2.0_L3.0/daily_data/CCMP_Wind*_V02.0_L3.0_RSS_uncompressed.nc"
    ExampleFileName = "CCMP_Wind_Analysis_20160522_V02.0_L3.0_RSS_uncompressed.nc"
    GetKeysRegex = r'CCMP_Wind_Analysis_(....)(..)(..)_V*.nc'

    Variable = 'Wind_Magnitude'   # to be computed as sqrt(uwnd^2 + vwnd^2)
    Mask = None
    Coordinates = ['time', 'latitude', 'longitude']    # time (len=4), winds every 6 hours during day

    OutputClimTemplate = ''

    @staticmethod
    def keysTransformer(s): return (ymd2doy(s[0], s[1], s[2]), s[0])      # DOY, YEAR

    @staticmethod
    def getKeys(url):
        return extractKeys(url, CCMPWind.GetKeysRegex, CCMPWind.keysTransformer)

    @staticmethod
    def split(seq, n):
        return [u for u in splitByNDaysKeyed(seq, n, CCMPWind.GetKeysRegex, CCMPWind.keysTransformer)]

    @staticmethod
    def genOutputName(doy, variable, nEpochs, averagingConfig):
        return "CCMP_Wind_Analysis_V02.0_L3.0_RSS_%03d_%dday_clim_%s" % (int(doy), nEpochs, averagingConfig['name'])


DatasetList = {'ModisSst': ModisSst, 'ModisChlor': ModisChlor,
               'MeasuresSsh': MeasuresSsh, 'CCMPWind': CCMPWind}


# Utils follow.
def ymd2doy(year, mon, day):
    return datetime2doy(ymd2datetime(year, mon, day))

def ymd2datetime(y, m, d):
    y, m, d = map(int, (y, m, d))
    return datetime.datetime(y, m, d)

def datetime2doy(dt):
    return int(dt.strftime('%j'))

def doy2datetime(year, doy):
    '''Convert year and DOY (day of year) to datetime object.'''
    return datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(doy) - 1)

def doy2month(year, doy): return doy2datetime(year, doy).strftime('%m')

