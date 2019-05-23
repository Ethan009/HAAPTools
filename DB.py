# coding:utf-8

from mongoengine import Document, connect
import GetConfig as gc
from mongoengine.fields import *
import datetime
import Source as s
import SANSW as sw
import HAAP as haap
from posix import lstat

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

def get_list_HAAP():
    """
    @note: HAAP-网页展示的数据
    """
    list_status = HAAP().query_last_record()
    if list_status:
        time = list_status.time
        status_to_show = list_status.status_to_show.values()
        return time,status_to_show
 
def get_HAAP_status():
    """
    @note:HAAP模块需调用的数据
    """
    all_status = HAAP().query_last_record()
    if all_status:
        return all_status.status_for_judging.values()

# SANSW
def switch_insert(n, origin, switch_summary, switch_status):
    """
    @note: SANSW数据插入
    """
    SANSW().insert(n, origin, switch_summary, switch_status)



def get_switch_total(list_switch_alias):
    """
    @note: SANSW模块调用-Total获取
    """

    list_switch = SANSW().query_first_records().switch_summary
    if list_switch:
        total = list_switch[list_switch_alias]["PE_Total"]
        return total


def get_switch_status():
    """
    @note: SANSW-网页部分展示
    """
    switch_status = SANSW().query_first_records()
    if switch_status:
        time = switch_status.time
        switch_summary = switch_status.switch_summary
        return time,switch_summary
 
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
    status_to_show = DictField()
    status_for_judging = DictField()


class collSANSW(Document):
    time = DateTimeField(default=datetime.datetime.now())
    origin = DictField()
    switch_summary = DictField()
    switch_status = DictField()


class collWarning(Document):
    time = StringField()
    level = IntField()
    ip = StringField()
    warn_message = StringField()
    confirm_status = IntField()


class HAAP(object):

    def insert(self, time_now, engine_status, lst_status):
        t = collHAAP(time=time_now, status_to_show=engine_status, status_for_judging=lst_status)
        t.save()

    def query_range(self, time_start, time_end):
        collHAAP.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')

    def query_last_record(self):
        return collHAAP.objects().order_by('-time').first()


class SANSW(object):

    def insert(self, time_now, origin, Summary, Switch_Status):
        t = collSANSW(time=time_now, origin=origin,
                      switch_summary=Summary, switch_status=Switch_Status)
        t.save()

    def query_range(self, time_start, time_end):
        collSANSW.objects(date__gte=time_start,
                          date__lt=time_end).order_by('-date')

    def query_first_records(self):
        return collSANSW.objects().order_by('-time').first()
   

class Warning(object):
    
    def insert(self, time_now, lstip, lstdj, lstSTS, confirm = 0):
        t = collWarning(time=time_now, ip=lstip, level=lstdj,
                        warn_message=lstSTS, confirm_status=confirm)
        t.save()
    
    def query_range(self, time_start, time_end):
        collWARN.objects(date__gte=time_start,
                        date__lt=time_end).order_by('-date')

    def query_first_records(self, intN):
        return collWARN.objects().order_by('-time').first()

    def update(self, intN):
        return collWARN.objects().order_by('-time').first()
    
    def get_all_unconfirm_warning(self):
        warning_status = collWarning.objects(confirm_status=0)
        return warning_status
    
    def update_Warning(self):
        return collWarning.objects(confirm_status=0).update(confirm_status=1)


if __name__ == '__main__':
    print(get_switch_total("SW01"))
    pass

