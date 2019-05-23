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
            'error_message': get_warning_unchecked_format()
        }
        return render_template("warning.html", **context)

    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)

    # 错误信息显示页面
    @app.route("/warning/")
    def warning():
        warning_unchecked = get_warning_unchecked_format()

        return render_template("warning.html",
                               error_message=warning_unchecked)

    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)


def haap_interval(intInterval):
    t = s.Timing()

    t.add_interval(haap.Check(), intInterval)
    t.stt()


xx[][]

yy = xx[]
dd = yy[]


# by klay
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


# by klay
def start_warn_check():


def thrd_web_rt():
    t1 = Thread(target=start_web, args=('rt',))
    t1.setDaemon(True)
    t1.start()
    try:
        while t1.isAlive():
            pass
    except KeyboardInterrupt:
        stopping_web(3)