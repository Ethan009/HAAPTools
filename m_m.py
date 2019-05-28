# coding:utf-8

from __future__ import print_function
import SANSW as sw
import HAAP as haap
import Source as s
from threading import Thread
from flask import Flask, render_template, request
import time
import SendEmail as SE
import datetime
import DB as db
import GetConfig as gc
try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

# <<<Get Config Field>>>
setting = gc.Setting()
interval_web_refresh = setting.interval_web_refresh()
interval_haap_update = setting.interval_haap_update()
interval_sansw_update = setting.interval_sansw_update()
interval_warning_check = setting.interval_warning_check()

swcfg = gc.SwitchConfig()
tuplThresholdTotal = swcfg.threshold_total()
lst_sansw_IP = swcfg.list_switch_IP()
lst_sansw_Alias = swcfg.list_switch_alias()

haapcfg = gc.EngineConfig()
oddEngines = haapcfg._odd_engines()
lst_haap_IP = oddEngines.values()
lst_haap_Alias = oddEngines.keys()
# <<<Get Config Field>>>


# <<web show table title>>
lstDescHAAP = ('Engine', 'IP', 'AH Status', 'Uptime',
               'Master', 'Cluster', 'Mirror')
lstDescSANSW = ('Switch', 'IP', 'Encout', 'DiscC3',
                'LinkFail', 'LossSigle', 'LossSync')
lstWarning = ('Time', 'Level', 'Device', 'IP', 'Message')


def monitor_rt_1_thread():
    t1 = Thread(target=start_web, args=('rt',))
    t1.setDaemon(True)
    t1.start()
    try:
        while t1.isAlive():
            pass
    except KeyboardInterrupt:
        stopping_web(3)


def monitor_db_4_thread():
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


def start_web(mode):
    '''
tlu = Time Last Update
    '''
    app = Flask(__name__, template_folder='./web/templates',
                static_folder='./web/static', static_url_path='')

    @app.route("/", methods=['GET', 'POST'])
    def home():

        # Transfer lstDescHAAP, lstDescSANSW, lstStatusHAAP, \
        # lstStatusSANSW, interval_refresh, haap_status, \
        # sansw_status, warning_status

        if mode == 'rt':
            StatusHAAP = haap.real_time_status()
            StatusSANSW = haap.real_time_status()
            tlu_haap = s.time_now_to_show()
            tlu_sansw = s.time_now_to_show()
            status_warning = 0

        elif mode == 'db':
            StatusHAAP = db.get_last_record_haap()
            StatusSANSW = db.get_last_record_sansw()
            tlu_haap = db.tlu_haap()
            tlu_sansw = db.tlu_sansw()
            status_warning = db.Status_Warning()

        return render_template("monitor.html",
                               Title_HAAP=lstDescHAAP,
                               Title_SANSW=lstDescSANSW,
                               StatusHAAP=lstStatusHAAP,
                               StatusSANSW=lstStatusSANSW,
                               haap_last_update=tlu_haap,
                               sansw_last_update=tlu_sansw,
                               status_haap=StatusHAAP,
                               status_sansw=StatusSANSW,
                               status_warning=status_warning)

    @app.route("/warning/")
    def warning():
        context = {
            'error_message': db.get_unconfirm_warning()
        }
        return render_template("warning.html", **context)

    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)


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


def haap_interval_check(intInterval):
    t = s.Timing()
    t.add_interval(check_all_haap(), intInterval)
    t.stt()

def sansw_interval_check(intInterval):
    t = s.Timing()
    t.add_interval(check_all_sansw(), intInterval)
    t.stt()

def warning_interval_check(intInterval):
    t = s.Timing()
    t.add_interval(warning_interval_check(), intInterval)
    t.stt()

###########################

# 根据需要重新写haap 和 sansw的方法，需要一个调用后直接可以输出judge需要的那个列表的方法。
# 同样，DB中也要写相应的方法

###########################

# def check_haap():
#     dicDB = db.haap_info_for_judge()
#     for i in range(len(lst_haap_Alias)):
#         lstRT = haap.info_for_judge(lst_haap_IP[i])
#         lstDB = dicDB[lst_haap_Alias[i]]
#         haap_judge(lstRT, lstDB)


# def check_haap():
#     def change_dic_to_list():
#         pass
    
#     dicDB = db.last_record()
#     objHAAP = haap.XXX()
#     info_for_DB = objHAAP.info_for_DB()
#     for i in range(len(lst_haap_Alias)):
#         lstRT = objHAAP.xxFun(lst_haap_IP[i])
#         lstDB = dicDB[lst_haap_Alias[i]]
#         haap_judge(lstRT, lstDB)

#     info = info_for_DB[0]
#     origin = info_for_DB[1]

#     db.haap_insert(info,origin)



# 现阶段先这样，每个引擎判断后发送邮件一次，下一阶段考虑两个引擎都判断完之后再发送邮件
# 这个获取get_engine_status_list_for_judg 的方法有些费劲啊，不如索性参考sansw的
def check_all_haap():
    Info_from_engine, Origin_from_engine = haap.data_for_db()
    Info_from_DB = db.get_HAAP_status() ### ***
    for i in range(len(lst_haap_Alias)):
#!!!!        list_judge = get_engine_status_list_for_judg(Info_from_engine,lst_haap_Alias[i])
        lstRT = haap.
        haap_judge(list_judge, Info_from_DB)
    db.haap_insert(s.time_now_to_show(),
                   Info_from_engine, Origin_from_engine)

def check_all_sansw():
    info_for_DB = sw.get_info_for_DB()
    for i in range(len(lst_sansw_Alias)):
        # get_Switch_Total 这玩意儿写了么。。。
        total_DB = db.get_Switch_Total(lst_sansw_Alias[i])
        sansw_total = get_total(info_for_DB, lst_sansw_Alias[i])
        judge_PE_total(total_DB, sansw_total, lst_sansw_IP[i])
    db.switch_insert(s.time_now_to_show(),
                     info_for_DB[0], info_for_DB[1], info_for_DB[2])


def warning_interval_check():
    unconfirm_warning = db.get_unconfirm_warning()
    if unconfirm_warning:
        lstXXX = change_to_list(unconfirm_warning)
        SE.send_warnmail(lstXXX)
    else:
        print('No Unconfirm Warning Found...')

# check status interval


class haap_judge(object):
    """docstring for haap_judge"""

    def __init__(self, statusRT, statusDB):
        self.host = statusRT[0]
        self.statusRT = statusRT
        self.statusDB = statusDB
        self.strTimeNow = s.time_now_to_show()
        self.lstWarningToSend = []
        #self.All_judge()

    def judge_AH(self, AHstatus_rt, AHstatus_db):
        if AHstatus_rt:
            if AHstatus_rt != AHstatus_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  level, 'engine', str_engine_AH)
                self.lstWarningToSend.apend(self.strTimeNow, self.host,
                               AH_errlevel, str_engine_AH)
                return
        return True

    def judge_reboot(self, uptime_second_rt, uptime_second_db):
        str_engine_restart = 'Engine Reboot %d secends ago'
        if uptime_second_rt <= uptime_second_db:
            restart_time = uptime_second_db - uptime_second_rt
            db.insert_warning(self.strTimeNow, self.host, 2,
                              'engine',  str_engine_restart%(restart_time))
            self.lstWarningToSend.apend(self.strTimeNow, self.host,
                           reboot_errlevel, str_engine_restart)

    def judge_Status(self, Status_rt, Status_db):
        if Status_rt:
            if Status_rt != Status_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  2, 'engine', str_engine_status)
                self.lstWarningToSend.apend(self.strTimeNow, self.host,
                               status_errlevel, str_engine_status)

    def judge_Mirror(self, MirrorStatus_rt, MirrorStatus_db):
        if MirrorStatus_rt:
            if MirrorStatus_rt != MirrorStatus_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  2, 'engine', str_engine_mirror)
                self.lstWarningToSend.apend(self.strTimeNow, self.host,
                               mirror_errlevel, str_engine_mirror)

    # 如果数据库没有信息，当引擎发生问题的时候，是否直接发送警报
    def All_judge(self):
        try:
            if self.statusDB:
                if self.judge_AH(self.statusRT[1], self.statusDB[1]):
                    self.judge_reboot(self.statusRT[2], self.statusDB[2])
                    self.judge_Status(self.statusRT[3], self.statusDB[3])
                    self.judge_Mirror(self.statusRT[4], self.statusDB[4])
        finally:
            SE.xxx(self.lstWarningToSend)

### engine_info[haap_Alias]这两个参数这么用的话，那么直接传入engine_info[haap_Alias]不是更好？
def get_engine_status_list_for_judg(engine_info, haap_Alias):
    list_info = engine_info[haap_Alias]
    list_status = list_info['status']
    list_status_judge = [list_status[i] for i in [0, 1, 4, 5]]
    list_status_judge.insert(2, list_status['up_sec'])
    return list_status_judge


def warning_message_sansw(intWarninglevel):
    if intWarninglevel == 1:
        strLevel = 'Notify'
    if intWarninglevel == 2:
        strLevel = 'Warning'
    if intWarninglevel == 3:
        strLevel = 'Alarm'
    return 'Total Error Count Increase Reach Level %s' % strLevel


#这玩意儿也可以写的更好呀
def judge_PE_total(total_sw, total_DB, sansw_IP):
    strTimeNow = s.time_now_to_show()
    if total_DB:
        intErrorIncrease = total_sw - total_DB
        intWarninglevel = s.is_Warning(intErrorIncrease, tuplThresholdTotal)
        if intWarninglevel:
            msg = warning_message_sansw(intWarninglevel)
            db.insert_warning(strTimeNow, sansw_IP, intWarninglevel,
                              'san_switch', msg)
            # 这部分发送应该是有一个特定的格式吧。。。
            SE.Timely_send([strTimeNow, sansw_IP, intWarninglevel,
                              'san_switch', msg])


