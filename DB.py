# coding:utf-8

import datetime

from mongoengine import Document, connect
from mongoengine.fields import *

import GetConfig as gc
import HAAP as haap
import SANSW as sw
import Source as s

# read config and connet to the datebase
cfgDB = gc.DBConfig()
strDBName = cfgDB.name()
# print("strDBName:", strDBName)
strDBHost = cfgDB.host()
# print("strDBName:", strDBHost)
intDBPort = cfgDB.port()
# print("strDBName:", intDBPort)

connect(strDBName, host=strDBHost, port=intDBPort)


# HAAP
def haap_insert(origin, info):
    """
    @note: monitoHAAP数据插入
    """
    HAAP().insert(origin, info)

    
def haap_last_record():
    """
    @note: HAAP最后一次所有的数据
    """
    return HAAP().query_last_record()


# ## 你这里是X也没有写啊！！！真是坑
def haap_judge_list():
    '''
[['1.1.1.1',0,8623,0,0],['1.1.1.1',0,8623,0,0]]
    '''
    dic_last = HAAP().query_last_record()

    list_info = engine_info[haap_Alias]
    list_status = list_info['status']
    list_status_judge = [list_status[i] for i in [0, 1, 4, 5]]
    list_status_judge.insert(2, list_status['up_sec'])
    return list_status_judge
    
    pass


def haap_judge_list_for_engineX(engineX):
    '''
['1.1.1.1',0,8623,0,0]
    '''
    # 找出engineX的index值，然后从judge_list()结果返回也可以
    
    pass


def haap_web_show_list():
    '''
[['1.1.1.1',0,'8d 7h 20s',0,0,0],['1.1.1.1',0,8623,0,0,0]]
    '''
    dic_last = HAAP().query_last_record()

    pass


def haap_web_show_for_engineX(engineX):
    '''
['1.1.1.1',0,'8d 7h 20s',0,0,0]
    '''
    # XXXXXXXX
    
    pass


# SANSW
def switch_insert(origin, sum_total, dicPEFormated):
    """
    @note: SANSW数据插入
    """
    SANSW().insert(origin,  sum_total, dicPEFormated)

    
def switch_last_info():
    """
    @note: SANSW最后一次所有的数据
    """
    return SANSW().query_last_records()


def sansw_web_show_list():
    pass


def sansw_total_list_or_dict():
    pass

 
# Warning 
def insert_warning(ip, level, warn_message, confirm):
    """
    @note: warning数据插入
    """
    Warning().insert(ip, level, warn_message, confirm)


def update_warning():
    """
    @note: 更新warning数据库
    """
    Warning().update_Warning()


def get_unconfirm_warning():
    """
    @note: warning网页部分展示
    """
    lstAllUCW = []
    for warning in Warning().get_all_unconfirm_warning():
        lstAllUCW.append([record.time, record.level, record.device, \
            record.ip, record.warn_message])
    if lstAllUCW:
        return lstAllUCW

            
class collHAAP(Document):
    time = DateTimeField(default=datetime.datetime.now())
    origin = DictField()
    info = DictField()


class collSANSW(Document):
    # ptes = port error show info formatted 
    time = DateTimeField(default=datetime.datetime.now())
    origin = DictField()
    ptes = DictField()
    sum_total = DictField()


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

    def insert(self, origin, info):
        t = collHAAP(origin=origin, info=info)
        t.save()

    def query_range(self, time_start, time_end):
        collHAAP.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')

    def query_last_record(self):
        return collHAAP.objects().order_by('-time').first()


class SANSW(object):

# ptes = port error show info formatted
    def insert(self, origin,  sum_total,ptes):
        t = collSANSW(origin=origin, sum_total=sum_total,ptes=ptes,)
        t.save()

    def query_range(self, time_start, time_end):
        collSANSW.objects(date__gte=time_start,
                          date__lt=time_end).order_by('-date')

    def query_last_records(self):
        return collSANSW.objects().order_by('-time').first()
   

class Warning(object):
    
    def insert(self, time_now, lstip, lstdj, device, lstSTS, confirm=0):
        t = collWarning(time=time_now, ip=lstip, level=lstdj, device=device,
                        warn_message=lstSTS, confirm=confirm)
        t.save()
    
    def query_range(self, time_start, time_end):
        collWARN.objects(date__gte=time_start,
                        date__lt=time_end).order_by('-date')

    def query_last_records(self):
        return collWARN.objects().order_by('-time').first()

    def update(self, intN):
        return collWARN.objects().order_by('-time').first()
    
    def get_all_unconfirm_warning(self):
        warning_status = collWarning.objects(confirm=0)
        return warning_status
    
    def update_Warning(self):
        return collWarning.objects(confirm=0).update(confirm=1)


if __name__ == '__main__':
    pass

