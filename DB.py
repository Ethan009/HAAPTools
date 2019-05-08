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
print("strDBName:", strDBName)
strDBHost = cfgDB.host()
print("strDBName:", strDBHost)
intDBPort = cfgDB.port()
print("strDBName:", intDBPort)

# <<<Get Config Field>>>
# HAAP
haapcfg = gc.EngineConfig()
list_engines_IP = haapcfg.list_engines_IP()[0]
telnet_port = haapcfg.telnet_port()
FTP_port = haapcfg.FTP_port()
passwd = haapcfg.password()
# switch
swcfg = gc.SwitchConfig()
list_sw_IP = swcfg.list_switch_IP()
list_sw_alias = swcfg.list_switch_alias()
ssh_port = swcfg.SSH_port()
user = swcfg.username()
passwd = swcfg.password()
list_sw_ports = swcfg.list_switch_ports()

connect(strDBName, host=strDBHost, port=intDBPort)

# intialize 3 collections


def get_dict_value(in_dict, target_key, results=[], not_d=True):
    for key in in_dict.keys():  
        data = in_dict[key] 
        if isinstance(data, dict):
            get_dict_value(data, target_key, results=results, not_d=not_d) 
        if key == target_key and isinstance(data, dict) != not_d:
            results.append(in_dict[key])
    return results

# HAAP
def haap_insert(n, engine_status,lst_status):
    """
    @note: HAAP数据插入
    """
    HAAP().insert(n, engine_status,lst_status)

def get_list_HAAP():
    """
    @note: HAAP 展示的数据
    """
    dbHAAP = HAAP()
    list_all_HAAP = dbHAAP.get_all_HAAP_status()
    lst_HAAP = list_all_HAAP[1]
    return lst_HAAP

def get_HAAP_uptime_second(list_HAAP_alias):
    """
    @note: HAAP  需调用的数据-uptime_second
    """
    dbHAAP = HAAP()
    list_all_HAAP = dbHAAP.get_all_HAAP_status()
    list_HAAP = list_all_HAAP[2]
    for key in list_HAAP.keys():
        if key == list_HAAP_alias:
            HAAP_uptime = get_dict_value(list_HAAP[key], 'uptime_second', results=[])
    return HAAP_uptime

def get_HAAP_mirror_status():
    """
    @note: HAAP  需调用的数据-mirror
    """
    dbHAAP = HAAP()
    list_all_HAAP = dbHAAP.get_all_HAAP_status()
    list_HAAP = list_all_HAAP[2]
    for key in list_HAAP.keys():
        if key == list_HAAP_alias:
            HAAP_uptime = get_dict_value(list_HAAP[key], 'mirror_status', results=[])
    return HAAP_uptime

def get_HAAP_cluster_status():
    """
    @note: HAAP  需调用的数据-cluster_status
    """
    dbHAAP = HAAP()
    list_all_HAAP = dbHAAP.get_all_HAAP_status()
    list_HAAP = list_all_HAAP[2]
    for key in list_HAAP.keys():
        if key == list_HAAP_alias:
            HAAP_uptime = get_dict_value(list_HAAP[key], 'cluster_status', results=[])
    return HAAP_uptime


# SANSW
def switch_insert(n, origin, switch_summary, switch_status):
    """
    @note: SANSW数据插入
    """
    SANSW().insert(n, origin, switch_summary, switch_status)


def get_switch_total(list_switch_alias):
    """
    @note: SANSW-Total获取
    """
    dbswitch = SANSW()
    list_all_switch = dbswitch.get_all_switch()
    list_switch = list_all_switch[2]
    for key in list_switch.keys():
        if key == list_switch_alias:
            switch_total = get_dict_value(list_switch[key], 'PE_Total', results=[])
    return switch_total

def get_list_switch():
    """
    @note: SANSW-网页部分展示
    """
    dbswitch = SANSW()
    list_all_switch = dbswitch.get_all_switch()
    list_switch = list_all_switch[2]
    return list_switch


# Warning 
def insert_warning(n, level, warn_message, confirm_status):
    """
    @note: warning数据插入
    """
    Warning().insert(n, level, warn_message, confirm_status)


def update_warning():
    """
    @note: 更新warning数据库
    """
    Warning().update_Warning()


def is_there_unconfirm_warning():
    """
    @note: warning展示数据
    """
    dbWarning = Warning()
    unconfirm_warnning = dbWarning.get_all_unconfirm_warning()
    if unconfirm_warnning:
        lstAllUCW = []
        for record in unconfirm_warnning:
            lstAllUCW.append([record.time, record.level, record.warn_message])
    return lstAllUCW
            
            
class collHAAP(Document):
    time = DateTimeField(default=datetime.datetime.now())
    engine_status = ListField()
    lst_status = DictField()


class collSANSW(Document):
    time = DateTimeField(default=datetime.datetime.now())
    origin = DictField()
    switch_summary = DictField()
    switch_status = DictField()


class collWarning(Document):
    time = DateTimeField(default=datetime.datetime.now())
    level = StringField()
    warn_message = StringField()
    confirm_status = IntField()


# DB opration of HAAP
class HAAP(object):

    def insert(self, time_now, engine_status, lst_status):
        t = collHAAP(time=time_now, engine_status = engine_status, lst_status = lst_status)
        t.save()

    def query_range(self, time_start, time_end):
        collHAAP.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')

    def query_last_record(self):
        return collHAAP.objects().order_by('-time').first()

    def query_time_of_first_records(self):
        return collHAAP.objects().order_by('-time').first()

    def get_all_HAAP_status(self):
        last_record = self.query_last_record()
        lst_all_status = [last_record.time,last_record.engine_status,
                          last_record.lst_status]
        return lst_all_status


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
   
    def get_all_switch(self):
        last_record = self.query_first_records()
        lstall = [last_record.time,last_record.origin,
                        last_record.switch_summary,last_record.switch_status]
        return lstall


class Warning(object):
    
    def insert(self, time_now, lstdj, lstSTS, confirm):
        t = collWarning(time=time_now, level=lstdj,
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
    pass

