# coding:utf-8

from mongoengine import Document
import GetConfig as gc

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
    Switch_status = DictField()
    Overview = DictField()


class collWarning(Document):
    time = DateTimeField(default=datetime.datetime.now())
    level = StringField()
    warn_message = StringField()
    confirm_status = IntField()


# DB opration of HAAP
class HAAP(object):
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

    def query_first_records(self, intN):
        return collHAAP.objects().order_by('-time').first()


class SANSW(object):

    '''
    "_id" : ObjectId("5ca45497ff237792f883aaef"),
    "time" : ISODate("2019-04-03T14:36:48.376Z"),

    SwitchShow:
    "SW_UP":{
    "IP":"1.1.1.1",
    

    OverView:{
    "SW_UP":{
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
        "1200", 
        "0", 
        "0", 
        "0", 
        "4"]
    }
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

    def insert(self, time_now, lstSW_IP, lstSWS, lstSW_Total):
        t = collSANSW(time=time_now, Switch_ip=lstSW_IP,
                      Switch_status=lstSWS, Switch_total=lstSW_Total)
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
   
    def update(self, time_now, lstdj, lstSTS, confirm):
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

if __name__ == '__main__':
    pass

    haap_db_opration = DB.HAAP()
    haap_db_opration.insert()

    SW_db_opration = DB.SW()
    SW_db_opration.insert()

