# coding:utf-8

import datetime
from posix import lstat

from mongoengine import Document, connect
from mongoengine.fields import *

import GetConfig as gc
import HAAP as haap
import SANSW as sw
import Source as s


# read config and connet to the datebase
cfgDB = gc.DBConfig()
strDBName = cfgDB.name()
#print("strDBName:", strDBName)
strDBHost = cfgDB.host()
#print("strDBName:", strDBHost)
intDBPort = cfgDB.port()
#print("strDBName:", intDBPort)

connect(strDBName, host=strDBHost, port=intDBPort)

# HAAP
def haap_insert(n, engine_status, lst_status):
    """
    @note: monitoHAAP数据插入
    """
    HAAP().insert(n, engine_status, lst_status)
    
def HAAP_last_info():
    """
    @note: HAAP最后一次所有的数据
    """
    return HAAP().query_last_record()

# SANSW
def switch_insert(n, origin, dicPEFormated, summary_total):
    """
    @note: SANSW数据插入
    """
    SANSW().insert(n, origin, dicPEFormated, summary_total)
    
def switch_last_info():
    """
    @note: SANSW最后一次所有的数据
    """
    return SANSW().query_last_records()

 
# Warning 
def insert_warning(n, ip, level, warn_message, confirm_status):
    """
    @note: warning数据插入
    """
    Warning().insert(n, ip, level, warn_message, confirm_status)


def update_warning():
    """
    @note: 更新warning数据库
    """
    Warning().update_Warning()


def get_unconfirm_warning():
    """
    @note: warning网页部分展示
    """
    unconfirm_warnning = Warning().get_all_unconfirm_warning()
    if unconfirm_warnning:
        lstAllUCW = []
        for record in unconfirm_warnning:
            lstAllUCW.append([record.time, record.ip, record.level, record.warn_message])
    return lstAllUCW

            
class collHAAP(Document):
    time = DateTimeField(default=datetime.datetime.now())
    origin = DictField()
    info = DictField()
    '''
origin:{'engine1':{'ip': '1.1.1.1', 'vpd': 'xxxx','engine': 'yyyy', 'mirror': 'yyyy'},
'engine2':{'ip': '1.1.1.1','vpd': 'xxxx','engine': 'yyyy', 'mirror': 'yyyy'}
}
info:{
    'engine1':{'status':['1.1.1.1',0,'2d','M',0,0],'up_sec':7283,'level':0},
    'engine2':{'status':['1.1.1.1',0,'2d','M',0,0],'up_sec':7283,'level':0}
}
    '''


class collSANSW(Document):
    time = DateTimeField(default=datetime.datetime.now())
    origin = DictField()
    dicPEFormated = DictField()
    summary_total = DictField()
    '''
origin:[{'ip':'x.x.x.x', 'porterrshow': 'xxxx','switchshow': 'yyyy'},
        {'ip':'x.x.x.x', 'porterrshow': 'xxxx','switchshow': 'yyyy'}]
dicPEFormated:[{'2': ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                '3': ['x', 'x', 'x', 'x', 'x', 'x', 'x']},
               {'2': ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                '3': ['x', 'x', 'x', 'x', 'x', 'x', 'x']}]
summary_total:[[6,7,5,4,2,8,27],
               [6,7,5,4,2,8,27]]

or

origin:{'sw1':{'ip':'x.x.x.x', 'porterrshow': 'xxxx','switchshow': 'yyyy'},
        'sw2':{'ip':'x.x.x.x', 'porterrshow': 'xxxx','switchshow': 'yyyy'}}
dicPEFormated:{'sw1':{'2': ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                '3': ['x', 'x', 'x', 'x', 'x', 'x', 'x']},
               'sw2':{'2': ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                '3': ['x', 'x', 'x', 'x', 'x', 'x', 'x']}}
summary_total:{'sw1':[6,7,5,4,2,8,27],
               'sw2':[6,7,5,4,2,8,27]}
    '''



class collWarning(Document):
    time = StringField()
    level = IntField()
    device = StringField()
    ip = StringField()
    msg = StringField()
    confirm = IntField()
    '''
time:'2019-05-20 15:20'
level:2
device: 'engine' or 'san switch'
ip:'1.1.1.1'
msg:'Engine Reboot 5 secends ago'
confirm:1
    '''


class HAAP(object):

    def insert(self, time_now, engine_status, lst_status):
        t = collHAAP(time=time_now, origin=engine_status, info=lst_status)
        t.save()

    def query_range(self, time_start, time_end):
        collHAAP.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')

    def query_last_record(self):
        return collHAAP.objects().order_by('-time').first()


class SANSW(object):

    def insert(self, time_now, origin, Switch_Status, Summary):
        t = collSANSW(time=time_now, origin=origin,
                       dicPEFormated=Switch_Status,summary_total=Summary)
        t.save()

    def query_range(self, time_start, time_end):
        collSANSW.objects(date__gte=time_start,
                          date__lt=time_end).order_by('-date')

    def query_last_records(self):
        return collSANSW.objects().order_by('-time').first()
   

class Warning(object):
    
    def insert(self, time_now, lstip, lstdj, device,lstSTS, confirm = 0):
        t = collWarning(time=time_now, ip=lstip, level=lstdj,device =device,
                        warn_message=lstSTS, confirm_status=confirm)
        t.save()
    
    def query_range(self, time_start, time_end):
        collWARN.objects(date__gte=time_start,
                        date__lt=time_end).order_by('-date')

    def query_last_records(self):
        return collWARN.objects().order_by('-time').first()

    def update(self, intN):
        return collWARN.objects().order_by('-time').first()
    
    def get_all_unconfirm_warning(self):
        warning_status = collWarning.objects(confirm_status=0)
        return warning_status
    
    def update_Warning(self):
        return collWarning.objects(confirm_status=0).update(confirm_status=1)


if __name__ == '__main__':
    pass

