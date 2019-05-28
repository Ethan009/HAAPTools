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
import types
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

# <<<email massage>>>





# <<web show-from name>>
lstDescHAAP = ('EngineIP', 'AH Status', 'Uptime',
               'Master', 'Cluster', 'Mirror')
lstDescSANSW = ('SwitchIP', 'Encout', 'DiscC3',
                'LinkFail', 'LossSigle', 'LossSync')
lstWarning = ('Time', 'Level', 'Message')


def show_engine_status_DB():
    engine = db.get_list_haap()
    return engine[0], engine[1]



def haap_status_for_judging(lstStatus,uptime_second):
    lstAllStatus=lstStatus
    lstStatus = [lstAllStatus[i] for i in [0,1,2,4,5]]
    lstStatus[2]=uptime_second
    return lstStatus


def start_mnt_4Thread():
    t1 = Thread(target=start_web, args=('db', interval_web_refresh))
    t2 = Thread(target=judge_haap_all_status, args=(interval_haap_update,))
    t3 = Thread(target=judge_SANSW_all_status, args=(interval_sansw_update,))
    t4 = Thread(target=send_unconfirm_waring, args=(interval_warning_check,))
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
    app = Flask(__name__, template_folder='./web/templates',
                static_folder='./web/static', static_url_path='')

    @app.route("/", methods=['GET', 'POST'])
    def home():
        if mode == 'rt':
            StatusHAAP = haap.list_status_for_realtime_show()
            #StatusSANSW = show_switch_status()
            tlu_haap = s.time_now_to_show()
            tlu_sansw = s.time_now_to_show()
        elif mode == 'db':
            tlu_haap = show_engine_status_DB()[0]
            tlu_sansw = show_switch_status_DB()[0]
            StatusHAAP = show_engine_status_DB()[1]
            StatusSANSW = show_switch_status_DB()[1]
        # 预警提示弹出为0，不弹出为1
        if request.method == 'GET' and get_warning_unchecked_format():
            error = 1
        else:
            db.update_warning()
            error = 0
        context = {
            'TitleHAAP': lstDescHAAP,
            'Titleswitch': lstDescSANSW,
            'StatusHAAP': StatusHAAP,
            'StatusSANSW': StatusSANSW,
            'tlu_haap': tlu_haap,
            'tlu_sansw': tlu_sansw,
            'error': error
        }
        return render_template("monitor.html", **context)

    @app.route("/warning/")
    def warning():
        context = {
            'error_message': get_warning_unchecked_format()
        }
        return render_template("warning.html", **context)

    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)


def judge_haap_all_status(interval_haap_update):
    t = s.Timing()
    t.add_interval(judge_all_haap, interval_haap_update)

    t.stt()


def judge_SANSW_all_status(interval_sansw_update):
    t = s.Timing()
    t.add_interval(get_sw_warning, interval_sansw_update)
    t.stt()


def judge_db_confirm(interval_warning_check):
    t = s.Timing()
    t.add_interval(judge_user_confirm, interval_warning_check)
    t.stt()


# def IP_to_alies(engine_IP):
#     for alies in list_haap_alias:
#         if list_haap_IP_alies[alies] == engine_IP:
#             return alies
#
#
# def list_to_dic(lstAllStatus):
#     dictAllStatus = {}
#     for lstStatus in lstAllStatus:
#         engine_alies = IP_to_alies(lstStatus[0])
#         dictAllStatus[engine_alies] = lstStatus
#     return dictAllStatus

def engineList_judge(engine_info, haap_Alias):
    list_info = engine_info[haap_Alias]
    list_status = list_info['status']
    list_status_judge = [list_status[i] for i in [0, 1, 4, 5]]
    list_status_judge.insert(2, list_status['up_sec'])
    return list_status_judge

def judge_all_haap():
    Info_from_engine, Origin_from_engine = haap.data_for_db()
    Info_from_DB = db.get_HAAP_status()
    for i in range(len(lst_haap_Alias)):
        listDB_judge = Info_from_DB[lst_haap_Alias[i]]
        listEngine_judge = engineList_judge(Info_from_engine,lst_haap_Alias[i])
        haap_judge(listEngine_judge, listDB_judge, lst_haap_Alias[i]).All_judge()
    db.haap_insert(s.time_now_to_show(),
                   Info_from_engine, Origin_from_engine)

# check status interval


class haap_judge(object):
    """docstring for haap_judge"""

    def __init__(self, statusRT, statusDB, haap_Alias):
        self.alias = haap_Alias
        self.host = statusRT[0]
        self.statusRT = statusRT
        self.statusDB = statusDB
        self.strTimeNow = s.time_now_to_show()
        self.lstWarningToSend = []

    def judge_AH(self, AHstatus_rt, AHstatus_db):
        str_engine_AH = 'Engine AH'
        if AHstatus_rt:
            if AHstatus_rt != AHstatus_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  2, 'engine', str_engine_AH)
                self.lstWarningToSend.apend([self.strTimeNow, self.host,
                               self.alias, str_engine_AH])
                return
        return True

    def judge_reboot(self, uptime_second_rt, uptime_second_db):
        str_engine_restart = 'Engine Reboot %d secends ago'
        if uptime_second_rt <= uptime_second_db:
            restart_time = uptime_second_db - uptime_second_rt
            db.insert_warning(self.strTimeNow, self.host, 2,
                              'engine',  str_engine_restart%(restart_time))
            self.lstWarningToSend.apend([self.strTimeNow, self.host,
                           self.alias, str_engine_restart])

    def judge_Status(self, Status_rt, Status_db):
        str_engine_status = 'Engine offline'
        if Status_rt:
            if Status_rt != Status_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  2, 'engine', str_engine_status)
                self.lstWarningToSend.apend([self.strTimeNow, self.host,
                               self.alias, str_engine_status])

    def judge_Mirror(self, MirrorStatus_rt, MirrorStatus_db):
        str_engine_mirror = 'Engine mirror not ok'
        if MirrorStatus_rt:
            if MirrorStatus_rt != MirrorStatus_db:
                db.insert_warning(self.strTimeNow, self.host,
                                  2, 'engine', str_engine_mirror)
                self.lstWarningToSend.apend([self.strTimeNow, self.host,
                               self.alias, str_engine_mirror])

    # 如果数据库没有信息，当引擎发生问题的时候，是否直接发送警报
    def All_judge(self):
        try:
            if self.statusDB:
                if self.judge_AH(self.statusRT[1], self.statusDB[1]):
                    self.judge_reboot(self.statusRT[2], self.statusDB[2])
                    self.judge_Status(self.statusRT[3], self.statusDB[3])
                    self.judge_Mirror(self.statusRT[4], self.statusDB[4])
        finally:
            if self.lstWarningToSend:
                SE.send_warnmail(self.lstWarningToSend)

# 执行查询数据库，并在发现用户未确认信息后，发送警报邮件


def send_unconfirm_waring():
    unconfirm_warning = db.get_unconfirm_warning()
    if unconfirm_warning:
        SE.send_warnmail(unconfirm_warning)
    else:
        print('No Unconfirm Warning Found...')


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


def warning_message_sansw(intWarninglevel):
    if intWarninglevel == 3:
        strLevel = 'Notify'
    if intWarninglevel == 2:
        strLevel = 'Warning'
    if intWarninglevel == 1:
        strLevel = 'Alarm'
    return 'Total Error Count Increase Reach Level %s' % strLevel


def judge_PE_total(total_sw, total_DB, sansw_IP, sansw_Alias):
    strTimeNow = s.time_now_to_show()
    if total_DB:
        intErrorIncrease = total_sw - total_DB
        intWarninglevel = s.is_Warning(intErrorIncrease, tuplThresholdTotal)
        if intWarninglevel:
            msg = warning_message_sansw(intWarninglevel)
            db.insert_warning(strTimeNow, sansw_IP, intWarninglevel,
                              'switch', warning_message_sansw(intWarninglevel))
            SE.send_warnmail([[strTimeNow, sansw_IP, sansw_Alias, msg]])

def get_sw_warning():
    info_for_DB = sw.get_info_for_DB()
    for i in range(len(lst_sansw_Alias)):
        total_DB = get_switch_total_db(lst_sansw_Alias[i])
        all_summary = info_for_DB[1]
        sansw_summary = all_summary[lst_sansw_Alias[i]]
        total_sansw = sansw_summary['PE_Total']
        judge_PE_total(total_DB, total_sansw, lst_sansw_IP[i], lst_sansw_Alias[i])
    db.switch_insert(s.time_now_to_show(),
                     info_for_DB[0], info_for_DB[1], info_for_DB[2])


    
# 最新方法


def get_switch_total_db(list_switch_alias):
    """
    @note: 获取数据库的Total
    """
    list_switch = db.switch_last_info().summary_total
    if list_switch:
        db_total = list_switch[list_switch_alias]["PE_Total"]
        return db_total

    
def get_switch_show_db():
    """
    @note: 获取数据库SANSW要展示的内容（时间，status）
    """
    lst_switch = db.switch_last_info()
    if lst_switch:
        time_switch = lst_switch.time
        lst_show_switch = [[i["IP"]] + i["PE_Sum"]for i in lst_switch.summary_total.values()]
        return time_switch,lst_show_switch


def get_HAAP_show_db():
    """
    @note: HAAP网页展示数据(时间，status)
    """
    lst_HAAP = db.HAAP_last_info()
    show_HAAP = []
    if lst_HAAP:
        time_HAAP = lst_HAAP.time
        for i in lst_HAAP.info.values():
            show_HAAP.append(i["status"])
            
    return time_HAAP,show_HAAP


def get_HAAP_other_db(lst_haap_Alias):
    """
    @note: 获取数据库具体up_sec
    ['192.168.1.1',0,27838,0,0]
    """
    lst_HAAP = db.HAAP_last_info().info
    if lst_HAAP:
        
        up_sec = lst_HAAP[lst_haap_Alias]["up_sec"]
    return up_sec



