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
SWTotal_level = swcfg.threshold_total()
sw_ID = swcfg.list_switch_alias()
list_sw_IP = swcfg.list_switch_IP()
haapcfg = gc.EngineConfig()
list_engines_IP = haapcfg.list_engines_IP()
list_haap_IP_alies = haapcfg._odd_engines()
list_haap_alies = haapcfg.list_engines_alias()

# <<<Get Config Field>>>

# <<<email massage>>>
str_engine_restart = 'Engine reboot'
str_engine_mirror = 'Engine mirror not ok'
str_engine_status = 'Engine offline'
str_engine_AH = 'Engine AH'
user_unconfirm = 0
mirror_level = 3
status_level = 3
uptime_level = 2
AH_level = 3

# <<web show-from name>>
lstDescHAAP = ('EngineIP', 'AH Status', 'Uptime',
               'Master', 'Cluster', 'Mirror')
lstDescSANSW = ('SwitchIP', 'Encout', 'DiscC3',
                'LinkFail', 'LossSigle', 'LossSync')
lstWarning = ('Time', 'Level', 'Message')


def current_time():
    return datetime.datetime.now()

def get_warning_unchecked_format():
    return db.get_unconfirm_warning()



def show_switch_status_DB():
    Switch = db.get_list_switch()
    lstSWSum=[[i["IP"]] + i["PE_Sum"]for i in Switch.values()]
    return lstSWSum

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


def start_web(mode):
    app = Flask(__name__, template_folder='./web/templates',
                static_folder='./web/static', static_url_path='')

    @app.route("/", methods=['GET', 'POST'])
    def home():
        if mode == 'rt':
            StatusHAAP = show_haap_status()
            StatusSANSW = 1
            tlu_haap = s.time_now_folder()
            tlu_sansw = s.time_now_folder()
        elif mode == 'db':
            StatusHAAP = show_db_haap_status()
            StatusSANSW = 1
            tlu_haap = db.get_HAAP_time()
            tlu_sansw = db.get_switch_time()
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


def real_haap(engine_IP):
    real_haap_info = haap.haap_status_real(engine_IP)
    return real_haap_info


def show_haap_status():
    lisHAAPstatus = []
    for engineIP in list_engines_IP:
        lisHAAPstatus.append(real_haap(engineIP)[0])
    return lisHAAPstatus


def show_db_haap_status():
    return db.get_list_HAAP().values()


def DB_haap_data(haap_alies, mode):
    if mode == 'uptime':
        return db.get_HAAP_uptime(haap_alies)
    elif mode == 'mirror':
        return db.get_HAAP_mirror(haap_alies)
    elif mode == 'status':
        return db.get_HAAP_status(haap_alies)
    elif mode == 'AH_status':
        return db.get_HAAP_AH_status(haap_alies)


def IP_to_alies(engine_IP):
    for alies in list_haap_alies:
        if list_haap_IP_alies[alies] == engine_IP:
            return alies

# 缺少获取引擎失败的处理机制
def judge_all_haap():
    status_to_show = {}
    status_for_judging = {}
    for engine_IP in list_engines_IP:
        haap_status = judge_haap(engine_IP)
        status_to_show[IP_to_alies(engine_IP)] = haap_status[0]
        status_for_judging[IP_to_alies(engine_IP)] = haap_status[1]
    db.insert_haap_status(
        s.time_now_folder(),
        status_to_show,
        status_for_judging)


def judge_haap(engine_IP):
    real_haap_info = real_haap(engine_IP)
    real_engine_status = real_haap_info[1]
    real_engine_status_web = real_haap_info[0]
    haap_alies = IP_to_alies(engine_IP)
    if real_engine_status[1] == 0:
        judge_uptime(
            engine_IP,
            real_engine_status[5],
            DB_haap_data(
                haap_alies,
                'uptime'))
        judge_mirror(
            engine_IP,
            real_engine_status[4],
            DB_haap_data(
                haap_alies,
                'mirror'))
        judge_status(
            engine_IP,
            real_engine_status[3],
            DB_haap_data(
                haap_alies,
                'status'))
    else:
        judge_AH_last(engine_IP, DB_haap_data(haap_alies, 'AH_status'))

    return real_engine_status_web, real_engine_status


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


def judge_AH_last(engine_IP, db_AH_status):
    if db_AH_status == 0:
        db.insert_warning(
            s.time_now_folder(),
            engine_IP,
            AH_level,
            str_engine_AH,
            user_unconfirm)
        # send email
    else:
        return


def judge_uptime(engine_IP, real_uptime, db_uptime):
    if real_uptime <= db_uptime:
        db.insert_warning(
            s.time_now_folder(),
            engine_IP,
            uptime_level,
            str_engine_restart,
            user_unconfirm)
        # send email
    else:
        return


def judge_mirror(engine_IP, real_mirror, db_mirror):
    if real_mirror == 0:
        return
    elif db_mirror != 0:
        return
    else:
        db.insert_warning(
            s.time_now_folder(),
            engine_IP,
            mirror_level,
            str_engine_mirror,
            user_unconfirm)
        # send email


def judge_status(engine_IP, real_status, db_status):
    if real_status is None:
        return
    elif db_status is not None:
        return
    else:
        db.insert_warning(
            s.time_now_folder(),
            engine_IP,
            status_level,
            str_engine_status,
            user_unconfirm)
        # send email

# 执行查询数据库，并在发现用户未确认信息后，发送警报邮件
def judge_user_confirm():
    if get_warning_unchecked_format():
        SE.send_warnmail(get_warning_unchecked_format())


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

sw_massage = "switch\'s error has reached"

def judge_PE_total(total_DB,total_sw,sw_IP):
    if total_DB:
        intlevel = s.is_Warning(total_sw - total_DB, SWTotal_level)
        if intlevel:
            db.insert_warning(s.time_now_to_show(),intlevel,sw_IP + sw_massage,confirm_status=0)
            e.send_warnmail([s.time_now_to_show(),intlevel,sw_IP + sw_massage])


def get_sw_warning():
    dic_all_sw = sw.get_dic_all_sw()
    for i in range(len(sw_ID)):
        total_DB = db.get_Switch_Total(sw_ID[i])
        all_sw_summary = dic_all_sw[1]
        sw_summary = all_sw_summary[sw_ID[i]]
        judge_PE_total(total_DB, sw_summary['PE_Total'],list_sw_IP[i])
    db.switch_insert(s.time_now_to_show(),dic_all_sw[0],dic_all_sw[1],dic_all_sw[2])


