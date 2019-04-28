# coding:utf-8

from mongoengine import Document, connect
import GetConfig as gc
from mongoengine.fields import *
import datetime


# read config and connet to the datebase
cfgDB = gc.DBConfig()
strDBName = cfgDB.name()
strDBHost = cfgDB.host()
intDBPort = cfgDB.port()

connect(strDBName, host=strDBHost, port=intDBPort)

# intialize 3 collections
 

class collHAAP(Document):
    time = DateTimeField(default=datetime.datetime.now())
    engine_status = ListField()


class collSANSW(Document):
    time = DateTimeField(default=datetime.datetime.now())
    origin = DictField()
    Summary = DictField()
    Switch_status = DictField()


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
            record_time = last_record[time]
            lstHAAPstatus = _convert_dict_to_list_HAAP(last_record[status])
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

    origin:
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
    "strPES":""
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
        t = collSANSW(time=time_now, Switch_origin=origin,
                      Switch_Summary=Summary,switch_status=Switch_Status)
        t.save()

    def query_range(self, time_start, time_end):
        collSANSW.objects(date__gte=time_start,
                          date__lt=time_end).order_by('-date')

    def query_all(self):
        return collSANSW.objects().order_by('-time')

    def query_N_records(self, intN):
        return collSANSW.objects().order_by('-time').limit(intN)

    def query_first_records(self, intN):
        return collSANSW.objects().order_by('-time').first()


class Warning(object):
    def insert(self, time_now, lstdj, lstSTS, confirm):
        t = collWARN(time=time_now, level=lstdj,
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
        warns = []
        a = collWARN.objects(confirm_status=0)
        for z in a:
            warns.append({'level':z.level, 'time':z.time, 'message':z.warn_message})
        return(warns)

    def update_Warning(self):
        update_Warning = collWARN.objects(confirm_status=0).update(confirm_status=1)
        


if __name__ == '__main__':
    pass

    last_update = Warning.get_recond()
    update_Warning = Warning.update_Warning()
    
    

    haap_db_opration = DB.HAAP()
    haap_db_opration.insert()

    SW_db_opration = DB.SW()
    SW_db_opration.insert()
    
    

