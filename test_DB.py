# coding:utf-8
from threading import Thread
import thread
import Source as s
import DB as db
import Monitor as mn
import datetime

"""
    注意注意：只要两个关键dict filed：origin 和 summary
    "_id" : ObjectId("5ca45497ff237792f883aaef"),
    "time" : ISODate("2019-04-03T14:36:48.376Z"),

 #     origin = {
#     "SW_UP":{
#     "IP":"1.1.1.1",
#     "switchshow":"",
#     "porterrshow":"",
#     },
#     "SW_Down":{
#     "IP":"1.1.1.1",
#     "switchshow":"",
#     "porterrshow":"",
#     }
#     }
#     Summary = {
#     "SW01":{
#     "IP":"1.1.1.1",
#     "PE_Sum":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "PE_Total":578
#     },
#     "SW02":{
#     "IP":"1.1.1.2",
#     "PE_Sum":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "PE_Total":578
#     }}
#     Switch_Status = {
#     "SW1":{
#     "IP":"1.1.1.1",
#     "PE":{
#     "0":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "1":[
#         "0", 
#         "0", 
#         "1.2", 
#         "0", 
#         "0", 
#         "0", 
#         "4"]
#     }},
#     "SW2":{
#     "IP":"2.2.2.2",
#     "PE":{
#     "0":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "1":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"]
# 
#     }}}
    """
    
"""

    "_id" : ObjectId("5cd3cfa6d6951a1b710f532e"),
    "time" : ISODate("2019-05-09T14:58:46.730Z"),
    "status_to_show" : {
        "engine1" : [ 
            "10.203.1.221", 
            0, 
            "1 Days 5 Hours 54 Minutes", 
            "M", 
            null, 
            0
        ],
        "engine0" : [ 
            "10.203.1.221", 
            0, 
            "1 Days 5 Hours 54 Minutes", 
            "M", 
            null, 
            0
        ]
    },
    "status_for_judging" : {
        "engine1" : [ 
            "10.203.1.221", 
            0, 
            "M", 
            null, 
            0, 
            107651
        ],
        "engine0" : [ 
            "10.203.1.221", 
            0, 
            "M", 
            null, 
            0, 
            107651
        ]
    }
}
[[IP1,encout,discc3,dfdf],[IP2,sss]]
    """
if __name__ == '__main__':
#     print(db.get_HAAP_status())
#     print(db.get_HAAP_status())
    
#     print(db.get_HAAP_status("engine1"))
#     Switch = db.get_list_switch()
#     lstSWSum=[[i["IP"]] + i["PE_Sum"]for i in Switch.values()]
#     print(lstSWSum)
#     
#     db.switch_insert(n,origin,Summary,Switch_Status)
#     db.haap_insert(datetime.datetime.now(),{'engine1':{'ip': '1.1.1.1', 'vpd': 'xxxx','engine': 'yyyy', 'mirror': 'yyyy'},
# 'engine2':{'ip': '1.1.1.1','vpd': 'xxxx','engine': 'yyyy', 'mirror': 'yyyy'}
# },{
#     'engine1':{'status':['1.1.1.1',0,'2d','M',0,0],'up_sec':7283,'level':0},
#     'engine2':{'status':['1.1.1.2',0,'2d','M',0,0],'up_sec':7283,'level':0}
# })
#     print(db.get_list_HAAP())
#     print(db.get_HAAP_time())
#     print(db.get_list_switch()["SW02"]["PE_Sum"])
#     print(db.get_switch_time())
#     print(db.get_HAAP_status("engine1"))
#     print(db.get_HAAP_mirror("engine1"))
#     print(db.get_HAAP_uptime("engine1"))
#     db.switch_insert(datetime.datetime.now(),{
#     "SW_UP":{
#     "IP":"1.1.1.1",
#     "switchshow":"",
#     "porterrshow":"",
#     },
#     "SW_Down":{
#     "IP":"1.1.1.1",
#     "switchshow":"",
#     "porterrshow":"",
#     }
#     },{
#     'SW01':{
#     'IP':"1.1.1.1",
#     "PE_Sum":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "PE_Total":578
#     },
#     "SW02":{
#     "IP":"1.1.1.2",
#     "PE_Sum":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "PE_Total":578
#     }},{
#     "SW1":{
#     "IP":"1.1.1.1",
#     "PE":{
#     "0":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "1":[
#         "0", 
#         "0", 
#         "1.2", 
#         "0", 
#         "0", 
#         "0", 
#         "4"]
#     }},
#     "SW2":{
#     "IP":"2.2.2.2",
#     "PE":{
#     "0":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"],
#     "1":[
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "0", 
#         "4"]
#   
#     }}})
#     print(db.get_switch_total("SW01"))
#     db.insert_warning(n,ip,level,warn_message,confirm_status)
#     print(db.get_unconfirm_warning())
#     print(db.get_switch_status())
#     print(db.switch_last_info().summary_total)
#     print(mn.get_switch_total_db("switch1"))
#     print(mn.get_switch_show_db())
    print(mn.get_HAAP_show_db())
#     print(mn.get_HAAP_other_db("engine1"))
    print("ok")
    pass
    
    
    
    
