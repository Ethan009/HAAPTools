# coding:utf-8
from threading import Thread
import thread
import Source as s
import DB as db
import M
import datetime

"""
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
    """
    
"""
        n = datetime.datetime.now()
    engine_status = [
        ['10.203.1.221',0,
        '1 Days 5 Hours 54 Minutes', 
        'M', None, 0, 107651],
        ['10.203.1.221', 0, 
         '1 Days 5 Hours 54 Minutes', 
         'M', None, 0, 107651]
        ]
    lst_status = {
        "HAAP1":{"ip":32313131,
         "ah":32313131,
         "uptime_second":32313131,
         "cluster_status":32313131,
         "mirror_status":32313131
            },
        "HAAP2":{"ip":2222222,
         "ah":32313131,
         "uptime_second":32313131,
         "cluster_status":32313131,
         "mirror_status":32313131
            }
        }
    
    """
if __name__ == '__main__':
    n = datetime.datetime.now()
    origin = {}
    Summary = {}
    Switch_Status = {}
    db.switch_insert(n,origin,Summary,Switch_Status)
    print("ok")
    pass
    
    
    
    
