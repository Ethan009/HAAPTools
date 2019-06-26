# coding:utf-8
import os
import sys
import time
import datetime
import re

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from collections import OrderedDict as odd

try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

import GetConfig as gc

import logging
logging.basicConfig()

# <<<Get Config Field>>>
setting = gc.Setting()
error_level = setting.message_level()

oddHAAPErrorDict = setting.oddRegularTrace()

# <<<Get Config Field>>>


def deco_OutFromFolder(func):
    strOriFolder = os.getcwd()

    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            # print(func.__name__, E)
            pass
        finally:
            os.chdir(strOriFolder)

    return _deco


def deco_Exception(func):

    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            print(func.__name__, E)

    return _deco


def time_now_folder():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def time_now_to_show():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def is_Warning(intValue, data):
    '''
    data is int or a tuple
    '''
    if isinstance(data, int):
        print('<>')
        if intValue > data:
            return True
    else:
        if intValue >= data[1]:
            return 2
        elif intValue >= data[0]:
            return 1
        else:
            return 0

def is_trace_level(num):
    if num in (1, 2, 3):
        return True


def is_IP(strIP):
    reIP = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if reIP.match(strIP):
        return True
    else:
        return False


def is_IP_list(lstIP):
    return all(map(is_IP, lstIP))


def is_file(strFileName):
    if os.path.isfile(strFileName):
        return True
    else:
        return False
    
def is_folder(strDirName):
    if os.path.isdir(strDirName):
        return True
    else:
        return False


def is_port(intPortNum):
    if type(intPortNum) == int:
        return True
    if type(intPortNum) == str:
        if intPortNum.isdigit():
            if type(eval(intPortNum)) == int:
                return True
    return False


def ShowErr(*argvs):
    '''
    Four argv:
    ClassName, FunctionName, MessageGiven, MessageRaised
    '''
    if len(argvs) == 3:
        argvs[3] = ''

    if error_level == 1:
        print(str('''
----------------------------------------------------------------------------
|*Error Message:                                                           |
|    Error Message: {:<55}|
|        {:<66}|
----------------------------------------------------------------------------\

'''.format(argvs[2], argvs[3])))
    elif error_level == 2:
        return ShowErr_level2(argvs)
    elif error_level == 3:
        print(str('''
----------------------------------------------------------------------------
|*Error Message:                                                           |
|    Class Name :   {:<55}|
|    Function name: {:<55}|
|    Error Message: {:<55}|
|        {:<66}|
----------------------------------------------------------------------------\

'''.format(argvs[0], argvs[1], argvs[2], argvs[3])))


def GotoFolder(strFolder):

    def _mkdir():
        if strFolder:
            if os.path.exists(strFolder):
                return True
            else:
                try:
                    os.makedirs(strFolder)
                    return True
                except Exception as E:
                    print('Create Folder "{}" Fail With Error:\n\t"{}"'.format(
                        strFolder, E))

    if _mkdir():
        try:
            os.chdir(strFolder)
            return True
        except Exception as E:
            print('Change to Folder "{}" Fail With Error:\n\t"{}"'.format(
                strFolder, E))


class Timing(object):

    def __init__(self):
        self.scdl = BlockingScheduler()

    def add_interval(self, job, intSec):
        trigger = IntervalTrigger(seconds=intSec)
        self.scdl.add_job(job, trigger)

    def add_once(self, job, rdate):
        try:
            self.scdl.add_job(job, 'date', run_date=rdate, max_instances=6)
        except ValueError as E:
            self.scdl.add_job(job, 'date')
        
    def stt(self):
        self.scdl.start()

    def stp(self):
        self.scdl.shutdown()


class TimeNow(object):

    def __init__(self):
        self._now = time.localtime()

    def y(self):  # Year
        return (self._now[0])

    def mo(self):  # Month
        return (self._now[1])

    def d(self):  # Day
        return (self._now[2])

    def h(self):  # Hour
        return (self._now[3])

    def mi(self):  # Minute
        return (self._now[4])

    def s(self):  # Second
        return (self._now[5])

    def wd(self):  # Day of the Week
        return (self._now[6])


def TraceAnalyse(strTraceFolder):
    import xlwt

    def _read_file(strFileName):
        try:
            with open(strFileName, 'r+') as f:
                strTrace = f.read()
            return strTrace.strip().replace('\ufeff', '')
        except Exception as E:
            print('Open File "{}" Failed With Error:\n\t"{}"'.format(
                strFileName, E))

    def _trace_analize(lstTraceFiles):
        intErrFlag = 0
        strRunResult = ''
        for strFileName in lstTraceFiles:
            if (lambda i: i.startswith('Trace_'))(strFileName):
                print('\n"{}"  Analysing ...'.format(strFileName))
                strRunResult += '\n"{}"  Analysing ...\n'.format(strFileName)
                openExcel = xlwt.Workbook()
                for strErrType in oddHAAPErrorDict.keys():
                    reErr = re.compile(oddHAAPErrorDict[strErrType])
                    tupErr = reErr.findall(_read_file(strFileName))
                    if len(tupErr) > 0:
                        strOut = ' *** "{}" Times of "{}" Found...'.format(
                            (len(tupErr) + 1), strErrType)
                        print(strOut)
                        strRunResult += strOut
                        objSheet = openExcel.add_sheet(strErrType)
                        for x in range(len(tupErr)):
                            for y in range(len(tupErr[x])):
                                objSheet.write(
                                    x, y, tupErr[x][y].strip().replace(
                                        "\n", '', 1))
                        intErrFlag += 1
                    reErr = None
                if intErrFlag > 0:
                    openExcel.save('TraceAnalyse_' + 
                                   strFileName + '.xls')
                else:
                    strOut = '--- No Error Find in "{}"'.format(strFileName)
                    print(strOut)
                    strRunResult += strOut
                intErrFlag = 0
        return strRunResult

    strOriginalFolder = os.getcwd()
    try:
        GotoFolder(strTraceFolder)
        lstTraceFile = os.listdir('.')
        _trace_analize(lstTraceFile)
    finally:
        os.chdir(strOriginalFolder)


if __name__ == '__main__':
    pass

