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

#HAAP
def haap_insert(self):
    HAAP().insert(n, lstSTS)

def is_there_HAAP():
    dbHAAP = HAAP()
    list_all_HAAP = dbHAAP.get_all_HAAP_status()
    return list_all_HAAP

#SANSW
def switch_insert(n, origin, switch_summary, switch_status):
    SANSW().insert()

def is_there_switch():
    dbswitch = SANSW()
    list_all_switch = dbswitch.get_all_switch()
    return list_all_switch

#Warning 
def insert_warning():
    Warning().insert(n, level, warn_message, confirm_status)

def update_warning():
    Warning().update_Warning()

def is_there_unconfirm_warning():
    dbWarning = Warning()
    unconfirm_warnning = dbWarning.get_all_unconfirm_warning()
    if unconfirm_warnning:
        lstAllUCW = []
        for record in unconfirm_warnning:
            lstAllUCW.append([record.time, record.level, record.warn_message])
            

class collHAAP(Document):
    time = DateTimeField(default=datetime.datetime.now())
    engine_status = DictField()


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
    
    # def __init__(self):
    #     self.last_record_list = get_last_record_list()
    #     self.time_engine_last_record = self.last_record_list[0]
    #     self.status_engine_last_record = self.last_record_list[1]

    def insert(self, time_now, lstSTS):
        t = collHAAP(time=time_now, engine_status=lstSTS)
        t.save()

    def query_range(self, time_start, time_end):
        collHAAP.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')

#     def query_all(self):
#         return collHAAP.objects().order_by('-time')
# 
#     def query_N_records(self, intN):
#         return collHAAP.objects().order_by('-time').limit(intN)

    def query_last_record(self):
        return collHAAP.objects().order_by('-time').first()

    def query_time_of_first_records(self):
        return collHAAP.objects().order_by('-time').first()

    def get_all_HAAP_status(self):
        last_record = self.query_last_record()
        lst_all_status = [last_record.time,last_record.engine_status]
        print(lst_all_status)
        return lst_all_status


class SANSW(object):

    '''
    注意注意：只要两个关键dict filed：origin 和 summary
    "_id" : ObjectId("5ca45497ff237792f883aaef"),
    "time" : ISODate("2019-04-03T14:36:48.376Z"),

    origin:{
    "SW_UP":{
    "IP":"1.1.1.1",
    "switchshow":""
    "porterrshow":""
    }
    "SW_Down":{
    "IP":"1.1.1.1",
    "switchshow":""
    "porterrshow":""
    }
    }

    Summary:{
    "SW01":{
    "IP":"1.1.1.1",
    "PE_Sum":[
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "4"]
    ]
    "PE_Total":578
    }
    "SW02":{
    "IP":"1.1.1.2",
    "PE_Sum":[
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "4"]
    ]
    "PE_Total":578
    }

    Switch_Status:{
    "SW1":{
    "IP":"1.1.1.1",
    "PE":{
    "0":[
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "4"],
    "1":[
        "0", 
        "0", 
        "1.2k", 
        "0", 
        "0", 
        "0", 
        "4"]
    }

    "SW_Down":{
    "IP":"2.2.2.2"
    "PE":{
    "0":[
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "4"],
    "1":[
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "0", 
        "4"]

    }
    '''

    def insert(self, time_now, origin, Summary, Switch_Status):
        t = collSANSW(time=time_now, origin=origin,
                      switch_summary=Summary, switch_status=Switch_Status)
        t.save()

    def query_range(self, time_start, time_end):
        collSANSW.objects(date__gte=time_start,
                          date__lt=time_end).order_by('-date')
# 
#     def query_all(self):
#         return collSANSW.objects().order_by('-time')
# 
#     def query_N_records(self, intN):
#         return collSANSW.objects().order_by('-time').limit(intN)

    def query_first_records(self):
        return collSANSW.objects().order_by('-time').first()
   
    def get_all_switch(self):
        last_record = self.query_first_records()
        lstall = [last_record.time, last_record.origin,
                last_record.switch_summary, last_record.switch_status]
        return lstall
    

class Warning(object):
    
    def insert(self, time_now, lstdj, lstSTS, confirm):
        t = collWarning(time=time_now, level=lstdj,
                        warn_message=lstSTS, confirm_status=confirm)
        t.save()
    
    def query_range(self, time_start, time_end):
        collWARN.objects(date__gte=time_start,
                        date__lt=time_end).order_by('-date')
# 
#     def query_all(self):
#         return collWARN.objects().order_by('-time')
# 
#     def query_N_records(self, intN):
#         return collWARN.objects().order_by('-time').limit(intN)

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
    # SANSW().get_all_switch()
  #  print(is_there_switch()[1])

    #is_there_HAAP()
    
    
    print("ok")
    pass

