# coding:utf-8

from mongoengine import Document, connect
import GetConfig as gc
from mongoengine.fields import *
import datetime
import Source as s
import SANSW as sw
import HAAP as haap


# read config and connet to the datebase
cfgDB = gc.DBConfig()
strDBName = cfgDB.name()
print("strDBName:", strDBName)
strDBHost = cfgDB.host()
print("strDBName:", strDBHost)
intDBPort = cfgDB.port()
print("strDBName:", intDBPort)

# <<<Get Config Field>>>
#HAAP
haapcfg = gc.EngineConfig()
list_engines_IP = haapcfg.list_engines_IP()[0]
telnet_port = haapcfg.telnet_port()
FTP_port = haapcfg.FTP_port()
passwd = haapcfg.password()
#switch
swcfg = gc.SwitchConfig()
list_sw_IP = swcfg.list_switch_IP()
list_sw_alias = swcfg.list_switch_alias()
ssh_port = swcfg.SSH_port()
user = swcfg.username()
passwd = swcfg.password()
list_sw_ports = swcfg.list_switch_ports()


connect(strDBName, host=strDBHost, port=intDBPort)

# intialize 3 collections

def _HAAP():
    return haap.Status(list_engines_IP, telnet_port,
                       passwd, FTP_port)

def _SW():
    return sw.Status(list_sw_IP, ssh_port,
                     user, passwd, list_sw_ports)
    

def get_from_haap_status():
    '''
    @author: paul
    @note: 获取引擎数据
    '''
    status = _HAAP()
    status = status.xxxxxxx()
    print("status.update_sss:",status)
    return status

def get_from_switch_status():
    '''
    @note: 获取交换机数据
    '''
    status = _SW()
    status = status.xxxxxxx()
    print("status.update_sss:",status)
    return status




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

    def query_all(self):
        return collHAAP.objects().order_by('-time')

    def query_N_records(self, intN):
        return collHAAP.objects().order_by('-time').limit(intN)

    def query_last_record(self):
        return collHAAP.objects().order_by('-time').first()

    def query_time_of_first_records(self):
        return collHAAP.objects().order_by('-time').first()

    def get_last_record_list(self):
        last_record = self.query_last_record()
        if last_record:
            record_time = last_record.time
            lstHAAPstatus = last_record.engine_status
            print("lstHAAPstatus:",lstHAAPstatus)
            return record_time, lstHAAPstatus
        else:
            return

    def time_engine_last_record():
        pass

    def status_engine_last_record():
        pass


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

    def query_all(self):
        return collSANSW.objects().order_by('-time')

    def query_N_records(self, intN):
        return collSANSW.objects().order_by('-time').limit(intN)

    def query_first_records(self):
        return collSANSW.objects().order_by('-time').first()
   
    def get_last_record_list(self):
        '''
        @note: 获取交换机数据
        '''
        last_record = self.query_first_records()
        if last_record:
            record_time = last_record.time
            lst_switch_origin = last_record.origin
            lst_switch_summary = last_record.switch_summary
            lst_switch_status = last_record.switch_status
            lstall = [record_time, lst_switch_origin, lst_switch_summary, lst_switch_status]
            return lstall
        else:
            return


class Warning(object):

    def insert(self, time_now, lstdj, lstSTS, confirm):
        t = collWarning(time=time_now, level=lstdj,
                     warn_message=lstSTS, confirm_status=confirm)
        t.save()
   
    def query_range(self, time_start, time_end):
        collWARN.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')
    def query_all(self):
        return collWARN.objects().order_by('-time')

    def query_N_records(self, intN):
        return collWARN.objects().order_by('-time').limit(intN)

    def query_first_records(self, intN):
        return collWARN.objects().order_by('-time').first()

    def update(self, intN):
        return collWARN.objects().order_by('-time').first()
    
    def get_recond(self):
        '''
        @note: 获取confirm_status为o的数据
        '''
        warns = []
        a = collWarning.objects(confirm_status=0)
        for z in a:
            warns.append({'level':z.level, 'time':z.time, 'message':z.warn_message})
        return(warns)
    
    def update_Warning(self):
        '''
        更新confirm_status  0 到 1
        '''
        update_Warning = collWarning.objects(confirm_status=0).update(confirm_status=1)
    
    def get_last_record_list(self):
        '''
        @note: 获取预警数据库信息
        '''
        last_record = self.get_recond()
        if last_record:
            lst_last_update = last_record
            return lst_last_update
        else:
            return
    
    
#####插入数据库
class insert_all(object):
    '''
    @author: paul
    @note: 插入数据库语句
    '''
    def switch_insert(self):
        SANSW().insert(n, origin, switch_summary, switch_status)
    
    def haap_insert(self):
        HAAP().insert(n, lstSTS)
     
    def warning_insert(self):
        Warning().insert(n, level, warn_message, confirm_status)


if __name__ == '__main__':
    get_from_switch_status()
    pass

