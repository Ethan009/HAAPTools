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
str_engine_restart = 'Engine reboot'
str_engine_mirror = 'Engine mirror not ok'
str_engine_status = 'Engine offline'
str_engine_AH = 'Engine AH'
user_unconfirm = 0

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

lstStatus, uptime_second = status_for_judging_realtime()
haap_status_for_judging(lstStatus, uptime_second)

a = db.get_haap_last()
info_engine1 = a.info['engnie1']
lst = info_engine1['status']
up_sec = info_engine1['up_sec']
haap_status_for_judging(lst,up_sec)


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
# <<<<<<< HEAD
#             StatusHAAP = haap.real_time_status_show()
#             # StatusSANSW = show_switch_status()
#             tlu_haap = s.time_now_folder()
#             tlu_sansw = s.time_now_folder()
# =======
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


def IP_to_alies(engine_IP):
    for alies in list_haap_alias:
        if list_haap_IP_alies[alies] == engine_IP:
            return alies


def list_to_dic(lstAllStatus):
    dictAllStatus = {}
    for lstStatus in lstAllStatus:
        engine_alies = IP_to_alies(lstStatus[0])
        dictAllStatus[engine_alies] = lstStatus
    return dictAllStatus


def judge_all_haap():
    SRT = haap.real_time_status()
    #IP,AHStatus,uptime_sec,cluster_status,mirror_status
    SDB = db.get_HAAP_status()
    SRT_show = haap.real_time_status_show()
    for i in range(len(list_haap_alias)):
        haap_judge(SRT[i], SDB[i])
    db.haap_insert(s.time_now_to_show(), list_to_dic(
        SRT_show), list_to_dic(SRT))

# check status interval


class haap_judge(object):
    """docstring for haap_judge"""

    def __init__(self, statusRT, statusDB):
        self.host = statusRT[0]
        self.statusRT = statusRT
        self.statusDB = statusDB
        self.All_judge()

    def judge_AH(self, AHstatus_rt, AHstatus_db):
        if AHstatus_rt:
            if AHstatus_rt != AHstatus_db:
                db.insert_warning(s.time_now_to_show(), self.host,
                                  reboot_errlevel, str_engine_restart, user_unconfirm)
                SE.Timely_send(s.time_now_to_show(), self.host,
                               AH_errlevel, str_engine_AH)
                return
        return True

    def judge_reboot(self, uptime_second_rt, uptime_second_db):
        if uptime_second_rt <= uptime_second_db:
            db.insert_warning(s.time_now_to_show(), self.host,
                              reboot_errlevel, str_engine_restart, user_unconfirm)
            SE.Timely_send(s.time_now_to_show(), self.host,
                           reboot_errlevel, str_engine_restart)

    def judge_Status(self, Status_rt, Status_db):
        if Status_rt:
            if Status_rt != Status_db:
                db.insert_warning(s.time_now_to_show(), self.host,
                                  status_errlevel, str_engine_status, user_unconfirm)
                SE.Timely_send(s.time_now_to_show(), self.host,
                               status_errlevel, str_engine_status)

    def judge_Mirror(self, MirrorStatus_rt, MirrorStatus_db):
        if MirrorStatus_rt:
            if MirrorStatus_rt != MirrorStatus_db:
                db.insert_warning(s.time_now_to_show(), self.host,
                                  mirror_errlevel, str_engine_mirror, user_unconfirm)
                SE.Timely_send(s.time_now_to_show(), self.host,
                               mirror_errlevel, str_engine_mirror)

    # 如果数据库没有信息，当引擎发生问题的时候，是否直接发送警报
    def All_judge(self):
        if self.statusDB:
            if self.judge_AH(self.lstStatusRT[1], self.lstStatusDB[1]):
                self.judge_reboot(self.lstStatusRT[2], self.lstStatusDB[2])
                self.judge_Status(self.lstStatusRT[4], self.lstStatusDB[4])
                self.judge_Mirror(self.lstStatusRT[5], self.lstStatusDB[5])

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


def judge_PE_total(total_sw, total_DB, sansw_IP):
    strTimeNow = s.time_now_to_show()
    if total_DB:
        intErrorIncrease = total_sw - total_DB
        intWarninglevel = s.is_Warning(intErrorIncrease, tuplThresholdTotal)
        if intWarninglevel:
            msg = warning_message_sansw(intWarninglevel)
            db.insert_warning(strTimeNow, sansw_IP, intWarninglevel, msg)
            # 这部分发送应该是有一个特定的格式吧。。。
            SE.Timely_send(strTimeNow, sansw_IP, intWarninglevel, msg)


def get_sw_warning():
    dic_all_sw = sw.get_dic_all_sw()
    for i in range(len(lst_sansw_Alias)):
        total_DB = db.get_Switch_Total(lst_sansw_Alias[i])
        sw_total = get_total(dic_all_sw, lst_sansw_Alias[i])
        judge_PE_total(total_DB, sw_total, lst_sansw_IP[i])
    db.switch_insert(s.time_now_to_show(),
                     dic_all_sw[0], dic_all_sw[1], dic_all_sw[2])
    
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
    @note: 获取数据库SANSW要展示的内容
    """
    lst_switch = db.switch_last_info().summary_total
    if list_switch:
        lst_show_switch = [[i["IP"]] + i["PE_Sum"]for i in list_switch.values()]
        return lst_show_switch


def get_HAAP_show_db():
    """
    @note: HAAP网页展示数据
    """
    lst_HAAP = db.HAAP_last_info().info
    show_HAAP = []
    if lst_HAAP:
        for i in lst_HAAP.values():
            show_HAAP.append(i["status"])
    return show_HAAP
    
