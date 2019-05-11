# coding:utf-8

from __future__ import print_function
import sys
import SANSW as sw
import HAAP as haap
import Source as s
from threading import Thread
from flask import Flask,render_template
import time
import SendEmail as SE

import datetime
import DB as db


try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

import GetConfig as gc

# <<<Get Config Field>>>
setting = gc.Setting()
interval_web_refresh = setting.interval_web_refresh()
interval_haap_update = setting.interval_haap_update()
interval_sansw_update = setting.interval_sansw_update()
interval_warning_check = setting.interval_warning_check()

swcfg = gc.SwitchConfig()
SWTotal_level=swcfg.threshold_total()
sw_ID=swcfg.list_switch_alias()

haapcfg = gc.EngineConfig()
list_engines_IP = haapcfg.list_engines_IP()
list_haap_IP_alies = haapcfg._odd_engines()
list_haap_alies = haapcfg.list_engines_alias()

# <<<Get Config Field>>>

##<<<email massage>>>
str_engine_restart='Engine reboot'
str_engine_mirror='Engine mirror not ok'
str_engine_status='Engine offline'
str_engine_AH='Engine AH'
user_unconfirm=0
mirror_level=3
status_level=3
uptime_level=2
AH_level=3

##<<web show-from name>>
lstDescHAAP = ('EngineIP', 'AH Status', 'Uptime',
               'Master', 'Cluster', 'Mirror')
lstDescSANSW = ('SwitchIP', 'EncOut', 'DiscC3',
                'LinkFail', 'LossSigle', 'LossSync')

def current_time():
    return datetime.datetime.now()


def get_warning_unchecked_format():
    unconfirm_info = db.get_unconfirm_warning()
    return unconfirm_info


def start_mnt_4Thread():
    t1 = Thread(target=start_web, args=('db', interval_web_refresh))
    t2 = Thread(target=judge_haap_all_status, args=(interval_haap_update,))
    t3 = Thread(target=judge_SANSW_all_status, args=(interval_sansw_update,))
    t4 = Thread(target=judge_db_confirm, args=(interval_warning_check,))

    t1.setDaemon(True)
    t2.setDaemon(True)
    t3.setDaemon(True)
    t4.setDaemon(True)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    try:
        while t4.isAlive():
            pass
        while t3.isAlive():
            pass
        while t2.isAlive():
            pass
        while t1.isAlive():
            pass
    except KeyboardInterrupt:
        stopping_web(3)


# need a funtion in Status() of HAAP.py , to judge warning status of engine
# same as HAAP.py



def start_web(mode):

#tlu = Time Last Update
    
    app = Flask(__name__, template_folder='./web/templates',
                static_folder='./web/static', static_url_path='')

    @app.route("/", methods=['GET', 'POST'])
    def home():

        if mode == 'rt':
            StatusHAAP = 
            StatusSANSW = 
            tlu_haap = 
            tlu_sansw = 
            status_warning = 

        elif mode == 'db':
            StatusHAAP =
            StatusSANSW = 
            tlu_haap = 
            tlu_sansw = 
            status_warning = 

        return render_template("monitor.html",
                               Title_HAAP=lstDescHAAP,
                               Title_SANSW=lstDescSANSW,

                               StatusHAAP=lstStatusHAAP,
                               StatusSANSW=lstStatusSANSW,
                               haap_last_update=tlu_haap,
                               sansw_last_update=tlu_sansw,
                               status_haap=status_haap,
                               status_sansw=status_sansw,
                               status_warning=status_warning)

    # 错误信息显示页面
    @app.route("/warning/")
    def warning():
        warning_unchecked = get_warning_unchecked_format()

        return render_template("warning.html",
                               error_message=warning_unchecked)

    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)




def judge_haap_all_status(interval_haap_update):
    t=s.Timing()
    t.add_interval(judge_all_haap, interval_haap_update)
    t.stt()

def judge_SANSW_all_status(interval_sansw_update):
    t = s.Timing()
    t.add_interval(get_sw_warning, interval_sansw_update)
    t.stt()

def judge_db_confirm(interval_warning_check):
    t=s.Timing()
    t.add_interval(judge_user_confirm, interval_warning_check)
    t.stt()


def real_haap(engine_IP):
    real_haap_info=haap.haap_status_real(engine_IP)
    return real_haap_info

def show_haap_status():
    pass


# def real_haap_web_show(engine_IP):
#     return real_haap(engine_IP)[0]
#
# def real_haap_judge(engine_IP):
#     return real_haap(engine_IP)[1]

def DB_haap_data(haap_alies,mode):
    if mode=='uptime':
        return db.get_HAAP_uptime(haap_alies)
    elif mode=='mirror':
        return db.get_HAAP_mirror(haap_alies)
    elif mode=='status':
        return db.get_HAAP_status(haap_alies)
    elif mode=='AH_status':
        return db.get_HAAP_AH_status(haap_alies)

def IP_to_alies(engine_IP):
    for alies in list_haap_alies:
        if list_haap_IP_alies[alies] == engine_IP:
            return alies

#缺少获取引擎失败的处理机制
def judge_all_haap():
    status_to_show={}
    status_for_judging={}
    for engine_IP in list_engines_IP:
        haap_status=judge_haap(engine_IP)
        status_to_show[IP_to_alies(engine_IP)]=haap_status[0]
        status_for_judging[IP_to_alies(engine_IP)]=haap_status[1]
    db.insert_haap_status(s.time_now_folder(),status_to_show ,status_for_judging)

def judge_haap(engine_IP):
    real_haap_info=real_haap(engine_IP)

    real_engine_status = real_haap_info[1]
    real_engine_status_web =real_haap_info[0]

    haap_alies = IP_to_alies(engine_IP)

    if real_engine_status[1] == 0:
        judge_uptime(engine_IP, real_engine_status[5], DB_haap_data(haap_alies, 'uptime'))
        judge_mirror(engine_IP, real_engine_status[4], DB_haap_data(haap_alies, 'mirror'))
        judge_status(engine_IP, real_engine_status[3], DB_haap_data(haap_alies, 'status'))

        # if judge_uptime(real_uptime,db_uptime):
        #     warning_info=judge_uptime(real_uptime,db_uptime)
        #     if warning_info:
        #         db.insert_warning(current_time ,engine_IP ,warning_info[0] ,warning_info[1] ,warning_info[2])
        #     #send email
        #
        # if judge_mirror(real_mirror,db_mirror):
        #     warning_info=judge_mirror(real_mirror,db_mirror)
        #     if warning_info:
        #         db.insert_warning(current_time ,engine_IP ,warning_info[0] ,warning_info[1] ,warning_info[2])
        #     #send email
        #
        # if judge_status(real_status,db_status):
        #     warning_info=judge_status(real_uptime,db_status)
        #     if warning_info:
        #         db.insert_warning(current_time ,engine_IP ,warning_info[0] ,warning_info[1] ,warning_info[2])
        #     #seng email

    else:
        judge_AH_last(engine_IP, DB_haap_data(haap_alies, 'AH_status'))

    return real_engine_status_web,real_engine_status


'''
def judge_haap(engine_IP):
    real_engine_status=real_haap(engine_IP)[1]
    haap_alies=IP_to_alies(engine_IP)
    
    real_uptime = real_engine_status[5]
    real_mirror = real_engine_status[4]
    real_status = real_engine_status[3]
    real_AH_status = real_engine_status[1]
    db_uptime = DB_haap_data(haap_alies, 'uptime')
    db_mirror = DB_haap_data(haap_alies, 'mirror')
    db_status = DB_haap_data(haap_alies, 'status')
    db_AH_status = DB_haap_data(haap_alies, 'AH_status')
    
    if real_AH_status==0:
        judge_uptime(engine_IP ,real_uptime ,db_uptime)
        judge_mirror(engine_IP ,real_mirror ,db_mirror)
        judge_status(engine_IP ,real_status ,db_status)

        # if judge_uptime(real_uptime,db_uptime):
        #     warning_info=judge_uptime(real_uptime,db_uptime)
        #     if warning_info:
        #         db.insert_warning(current_time ,engine_IP ,warning_info[0] ,warning_info[1] ,warning_info[2])
        #     #send email
        #
        # if judge_mirror(real_mirror,db_mirror):
        #     warning_info=judge_mirror(real_mirror,db_mirror)
        #     if warning_info:
        #         db.insert_warning(current_time ,engine_IP ,warning_info[0] ,warning_info[1] ,warning_info[2])
        #     #send email
        #
        # if judge_status(real_status,db_status):
        #     warning_info=judge_status(real_uptime,db_status)
        #     if warning_info:
        #         db.insert_warning(current_time ,engine_IP ,warning_info[0] ,warning_info[1] ,warning_info[2])
        #     #seng email

    else:
        judge_AH_last(engine_IP ,db_AH_status)
'''


#haal_alies = IP_to_alies(engine_IP)

def judge_AH_last(engine_IP,db_AH_status):
    if db_AH_status==0:
        db.insert_warning(s.time_now_folder() ,engine_IP ,AH_level ,str_engine_AH ,user_unconfirm )
        #send email


def judge_uptime(engine_IP,real_uptime,db_uptime):
    if real_uptime<=db_uptime:
        db.insert_warning(s.time_now_folder() ,engine_IP ,uptime_level ,str_engine_restart ,user_unconfirm )
        #send email
    else:
        return


def judge_mirror(engine_IP,real_mirror,db_mirror):
    if real_mirror==0:
        return
    elif db_mirror!=0:
        return
    else:
        db.insert_warning(s.time_now_folder() ,engine_IP ,mirror_level ,str_engine_mirror ,user_unconfirm )
        #send email

def judge_status(engine_IP,real_status,db_status):
    if real_status==None:
        return None
    elif db_status!=None:
        return None
    else:
        db.insert_warning(s.time_now_folder() ,engine_IP ,status_level ,str_engine_status ,user_unconfirm )
        #send email

# def to_haap_status_db(status_to_show ,status_for_judging):
#     db.insert_haap_status(current_time(),status_to_show,status_for_judging)



# def judge_AH(real_AH_status):
#     if real_AH_status==0:
#         return 0
#     else :
#         return None


#执行查询数据库，并在发现用户未确认信息后，发送警报邮件
def judge_user_confirm():
    #[[time,IP,level,massage],[],[]]
    if get_warning_unchecked_format():
        SE.send_warnmail(get_warning_unchecked_format())

'''
def job_update_interval(intInterval):
    t = s.Timing()
    db = DB_collHAAP()

    def do_it():
        # print(get_HAAP_status_list()[0],'8888888888888')
        n = datetime.datetime.now()
        do_update = db.haap_insert(n, get_HAAP_status_list())
        # print('update complately...@ %s' % n)
        return do_update
    t.add_interval(do_it, intInterval)
    t.stt()

confirm_status = 0


def job_update_interval_haap(intInterval):
    t = s.Timing()
    db = DB_collHAAP()

    def do_it():
        n = datetime.datetime.now()
        # print(get_HAAP_status_list()[2])

        a = get_HAAP_status_list()
        # do_update = db.haap_insert(n, a[0])
        db.haap_insert(n, a[0])
        if a[2] != []:
            for i in range(len(a[2])):

                # do_update = db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                # print('update complately...@ %s' % n)
            warnlist = a[1]
            warnlevel = a[2]
            email.Timely_send(warnlist, warnlevel)

    t.add_interval(do_it, 10)
    t.stt()


# #线程3交换机的
def job_update_interval_switch(intInterval):
    t = s.Timing()
    db = DB_collHAAP()

    def do_it():
        n = datetime.datetime.now()
        a = get_Switch_Total()
        # do_update_Switch = db.Switch_insert(n, get_Switch_IP(), get_Switch_status_list(), a[0])
        db.Switch_insert(n, get_Switch_IP(), get_Switch_status_list(), a[0])
        if a[1] != []:
            for i in range(len(a[2])):
                # do_update = db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                print("qqq", qqq)
                # print('update complately...@ %s' % n)
            warnlist = a[1]
            warnlevel = a[2]
            email.Timely_send(warnlist, warnlevel)

    t.add_interval(do_it, 10)
    t.stt()


# 线程4发送邮件
def job_update_interval_email(intInterval):
    t = s.Timing()
    db = DB_collHAAP()

    def do_it():
        warninfo = email.send_warnmail(mailto_list, sub, get_all_recond())
        # print('ddf',warninfo)
        return warninfo

    t.add_interval(do_it, intInterval)
    t.stt()
'''

def stopping_web(intSec):
    try:
        print('\nStopping Web Server ', end='')
        for i in range(intSec):
            time.sleep(1)
            print('.', end='')
        time.sleep(1)
        print('\n\nWeb Server Stopped.')
    except KeyboardInterrupt:
        print('\n\nWeb Server Stopped.')


def thrd_web_rt():
    t1 = Thread(target=start_web, args=('rt',))
    t1.setDaemon(True)
    t1.start()
    try:
        while t1.isAlive():
            pass
    except KeyboardInterrupt:
        stopping_web(3)
massage=''

def get_sw_warning():
    dic_all_sw = sw.get_dic_all_sw()
    for i in sw_ID:
        total_DB = db.get_Switch_Total(i)
        if total_DB:
            total=dic_all_sw[1][i]['PE_Total'] - total_DB
            intlevel=s.is_Warning(total,SWTotal_level)
            if intlevel:
                db.insert_warning(time,intlevel,massage,confirm_status)
                #send email
    db.switch_insert(dic_all_sw[0][0],dic_all_sw[0][1],dic_all_sw[0][2])


# time:xxxxxxxxx
# engine_status = {
#         'engine0':['10.203.1.221',0,
#         '1 Days 5 Hours 54 Minutes',
#         'M', None, 0],
#         'engine1':['10.203.1.221', 0,
#          '1 Days 5 Hours 54 Minutes',
#          'M', None, 0]
#         }
# lst_status = {
#         'engine0':['10.203.1.221',0,
#         'M', None, 0, 107651],
#         'engine1':['10.203.1.221', 0,
#          'M', None, 0, 107651]
#         }