# coding:utf-8

from __future__ import print_function
import sys
import SANSW as sw
import HAAP as haap
import Source as s
import Thread

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


# <<<Get Config Field>>>

def get_warning_unchecked_format():
    pass

def get_status_haap():
    return db.HAAP



def start_mnt_4Thread():
    t1 = Thread(target=start_web, args=('db', interval_web_refresh))
    t2 = Thread(target=haap, args=(interval_haap_update,))
    t3 = Thread(target=sansw, args=(interval_sansw_update,))
    t4 = Thread(target=email_warning, args=(interval_warning_check,))

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


lstDescHAAP = ('EngineIP', 'AH Status', 'Uptime',
               'Master', 'Cluster', 'Mirror')
lstDescSANSW = ('SwitchIP', 'EncOut', 'DiscC3',
                'LinkFail', 'LossSigle', 'LossSync')
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


def haap(interval_haap_update):
    pass

def sansw(interval_sansw_update):
    pass

def email_warning(interval_warning_check):
    pass

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
