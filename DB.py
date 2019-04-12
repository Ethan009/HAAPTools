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
    Switch_ip = DictField()
    Switch_status = DictField()
    Switch_total = DictField()


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

    def query_range(self, time_start, time_end):
        collWARN.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')

    def query_all(self):
        return collWARN.objects().order_by('-time')

    def query_N_records(self, intN):
        return collWARN.objects().order_by('-time').limit(intN)

    def query_first_records(self, intN):
        return collWARN.objects().order_by('-time').first()
