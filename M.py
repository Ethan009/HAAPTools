# coding:utf-8

from __future__ import print_function
import SANSW as sw
import HAAP as haap
import DB as db
import Source as s
from collections import OrderedDict as Odd
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import sys
import datetime
import time
import getpass
import re
from mongoengine import *
from threading import Thread
import thread
import email_form as email
from flask import Flask, render_template, redirect, request

try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

import GetConfig as gc

# <<<Help String Feild>>>
strHelp = '''
        Command           Description

        ptes                    : Print Port Error of Defined SAN Switch Ports
        ptcl <IP Port> | all    : Clear Port Error Counter for Given Port on Given SAN switch
        # ptclALL                 : Clear Port Error Counter for All Ports on All Defined SAN switches
        sws <IP> | all           : Print switchshow Info for Given SAN Switch
        # swsALL         : Print switchshow Info for All Defined SAN Switches
        gt             : Get Trace of All Defined Engine(s), Save in {trace} Folder
        anls <Folder> | all          : Analyse Trace of All Defined Engine(s)
        # anlsTrace      : Analyze Trace Files under <Folder>
        bk <IP> | all          : Backup Config for All Defined Engine(s), Save in {cfg} Folder
        ec             : Execute Commands listed in <File> on Given Engine
        pc <sw|haap IP> |all            : Execute Periodic Check on Given Engine, Save in {pc} Folder
        # pcsw           : Execute Periodic Check on Given Switch, Save in {pc} Folder
        # pcALL          : Execute Periodic Check on All Defined Engine(s), Save in {pc} Folder
        cfw          : Change Firmware for Given Engine
        sts <IP> | all            : Show Overall Status for All Engines
        st  <IP> | all           : Sync Time with Local System For All Engines
        stm  <IP> | all          : Get Time of All Defined Engine(s)
        wrt            : Start Web Update Real Time
        wdb            : Start Web Update from DataBase
        # sancheck       : san check
        # swc            : start warning check
        '''

strPTCLHelp = '''
    ptcl <Switch_IP> <Port_Num>
'''

strSWSHelp = '''
    sws <Switch_IP> 
'''

strAutoCLIHelp = '''
    ec <Engine_IP> <Command_File>
'''

strPCHelp = '''
    pc <Engine_IP>
'''

strPCSWHelp = '''
    pcsw <Switch_IP>
'''

strHelpAnalyseTrace = '''
    anlsTrace <Trace_Folder>
'''

strHelpUpdateFW = '''
    chgFW <Engine_IP> <Firmware_File>
'''

strHelpSingleCommand = '''
    {}
'''
# <<<Help String Field>>>

# <<<Help String Field>>>


# Config of HAAP
HAAP_Config = gc.EngineConfig()
lstHAAP = HAAP_Config.list_engines_IP()
lstHAAPAlias = HAAP_Config.list_engines_alias()
intTNPort = HAAP_Config.telnet_port()
intFTPPort = HAAP_Config.FTP_port()
strHAAPPasswd = HAAP_Config.password()
intTraceLevel = HAAP_Config.trace_level()
# Config of SANSW
SANSW_Config = gc.SwitchConfig()
lstSANSWAlias = SANSW_Config.list_switch_alias()
intSWSSHPort = SANSW_Config.ssh_port()
strSWUser = SANSW_Config.sw_username()
strSWPWD = SANSW_Config.sw_password()
dicSANSWPor = SANSW_Config.list_switch_ports()

# Config of DB



# Config of Setting

# oddTraceRegular
# strDesFolder
# strPCFolder
# lstCommand_PC_HAAP
# lstCommand_PC_SANSW

# refresh_interval = gc.Setting.monitor_web_refresh()

def _get_TimeNow_Human():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _get_TimeNow_Folder():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Initialize HAAP ...
def _HAAP_Action(strEngineIP):
    return haap.Action(strEngineIP, intTNPort, strHAAPPasswd, intFTPPort)


def _HAAP_Status(strEngineIP):
    return haap.Status(strEngineIP, intTNPort, strHAAPPasswd, intFTPPort)


def get_HAAP_over_all():
    odd = Odd()
    for i in len(range(lstHAAP)):
        odd[lstHAAPAlias[i]] = _HAAP_Status(lstHAAP[i]).over_all()
    return odd

def _convert_dict_to_list_HAAP(odd):
    lstHAAPstatus = []
    for i in range(len(odd)):
        lstOneEngine = []
        lstOneEngine.append(odd.keys(i))
        for status in odd[i]:
            lstOneEngine.append(status)
        lstHAAPstatus.append(lstOneEngine)
    return lstHAAPstatus



def get_HAAP_ditInfo():
    odd = Odd()
    for i in len(range(lstHAAP)):
        odd[lstHAAPAlias[i]] = _HAAP_Status(lstHAAP[i]).dictInfo
    return odd


# Initialize The SAN Switch ...
def _SANSW_Status(strSWIP, lstSWPorts):
    return sw.Status(strSWIP, intSWSSHPort,
                    strSWUser, strSWPWD, lstSWPorts)

def _SANSW_Action(strSWIP, lstSWPorts):
    return sw.Status(strSWIP, intSWSSHPort,
                    strSWUser, strSWPWD, lstSWPorts)

def get_SANSW_origin():
    ### 需要在sansw里面写一个获取origin data的方法。获取到一个字典里面有三个键，分别是
    ### IP, switchshow, porterrshow
    odd = Odd()
    for i in len(range(lstSANSW)):
        odd[lstSANSWAlias[i]] = _SANSW_Status(lstSANSW[i]).origin()
    print("odd:",odd)
    return odd

def get_SANSW_summary():
    ### 需要在sansw里面写一个获取summary的方法。获取到一个字典里面有三个键，分别是
    ### IP, ''格式化（并且字符到数字转换）之后的porterrshow''(不确定要不要), 各种错误总数列表，以及总和值
    odd = Odd()
    for i in len(range(lstSANSW)):
        odd[lstSANSWAlias[i]] = _SANSW_Status(lstSANSW[i]).summary()
    return odd

def show_SANSW_error():
    ### 需要在sansw里面写一个显示（打印）porterrshow的方法。用原始值（字符，包含m，k的）
    for i in len(range(lstSANSW)):
        _SANSW_Status(lstSANSW[i]).show_error()


# analyze trace files under DesFolder, results saved in .xsl files
def _TraceAnalyse(strDesFolder):
    s.TraceAnalyse(oddTraceRegular, strDesFolder)

# execute periodic-check commands (defined in Config.ini),\
# print and save results in PCFolder

def _PC_HAAP(strEngineIP):
    _HAAP_Action(strEngineIP).periodic_check(lstCommand_PC_HAAP,
                                      strPCFolder,
                                      'PC_{}_HAAP_{}.log'.format(
                                          _get_TimeNow_Folder(), strEngineIP))


def _PC_SANSW(strSANSWIP):
    _SANSW_Action(strEngineIP).periodic_check(lstCommand_PC_SANSW,
                                      strPCFolder,
                                      'PC_{}_SANSW_{}.log'.format(
                                          _get_TimeNow_Folder(), strSANSWIP))

# execute cmds in file and print the results
def _AutoCLI(strEngineIP, CMDFile):
    _HAAP_Action(strEngineIP).execute_multi_command(CMDFile)


def _change_firmware(strEngineIP, strFWFile):
    _HAAP_Action(strEngineIP).updateFW(strFWFile)


# update DB

# query from DB
tupHAAP_last_record = db.HAAP.get_last_record_list()
if tupHAAP_last_record:
    time_engine_last_record = tupHAAP_last_record[0]
    status_engine_last_record = tupHAAP_last_record[1]
else:
    time_engine_last_record = _get_TimeNow_Human()
    status_engine_last_record = None


### 需要db.SANSW配合写类似 get_last_record_list 方法
tupSANSW_last_record = db.SANSW.get_last_record_list()
if tupSANSW_last_record:
    time_SANSW_last_record = tupSANSW_last_record[0]
    status_SANSW_last_record = tupSANSW_last_record[1]
else:
    time_SANSW_last_record = _get_TimeNow_Human()
    status_SANSW_last_record = None


def start_web(mode):
    app = Flask(__name__, template_folder='./web/templates',
                static_folder='./web/static', static_url_path='')

### 写在网页里面
    lstDesc = ('EngineIP', 'Status', 'Uptime', 'Master', 'Cluster' 'Mirror')
    lstDesc_switches = ('SwitchIP', 'Encout', 'Discc3', 'Link Fail', 'Loss Sigle', 'Loss Sync')
    

    @app.route("/", methods=['GET', 'POST'])
    def home():
        refresh_interval = refresh_interval
        if mode == 'rt':
            refresh_time = _get_TimeNow_Human()
            engine_refresh_time = refresh_time
            switch_refresh_time = refresh_time
            Status=Status,
            Status_switch=Status_switch,
            warns=warns

        elif mode == 'db':
            refresh_time = _get_TimeNow_Human()
            engine_refresh_time = time_engine_last_record
            switch_refresh_time = refresh_time
            Status=status_engine_last_record,
            Status_switch=Status_switch,
            warns=warns

        return render_template("monitor.html",
                               engine_refresh_time=engine_refresh_time,
                               switch_refresh_time=switch_refresh_time,
                               Status=Status,
                               Status_switch=Status_switch,
                               timeup=refresh_interval,
                               warns=warns)

    # 错误信息显示页面
    @app.route("/warning/")
    def warning():
        error_message = get_all_recond()

        return render_template("warning.html",
                               error_message=error_message)

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
                print("qqq",qqq)
                # print('update complately...@ %s' % n)
            warnlist = a[1]
            warnlevel = a[2]
            email.Timely_send(warnlist, warnlevel)

    t.add_interval(do_it,10)
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
    t1 = Thread(target=start_web, args=('db',))
    t2 = Thread(target=job_update_interval_haap, args=(10,))
    t3 = Thread(target=job_update_interval_switch, args=(10,))
    t4 = Thread(target=job_update_interval_email, args=(20 * 360,))

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


def thrd_web_rt():
    t1 = Thread(target=start_web, args=('rt',))
    t1.setDaemon(True)
    t1.start()
    try:
        while t1.isAlive():
            pass
    except KeyboardInterrupt:
        stopping_web(3)



def main():
    # get_wc()
    # _get_SWInstance()
    # _get_HAAPInstance()
    if len(sys.argv) == 1:
        print(strHelp)
        # print ('aaaaaa',len(sys.argv))

    elif sys.argv[1] == 'ptes':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('ptes'))
        elif not _checkIPlst(lstSW):
            print('IP error. Please check Switch IPs defined in "Conf.ini"')
        else:
            for i in range(len(lstSW)):
                _SW(lstSW[i], lstSWPorts[i]).show_porterrors()

    elif sys.argv[1] == 'ptcl':
        if len(sys.argv) != 4:
            print(strPTCLHelp)
        elif not _isIP(sys.argv[2]):
            print('IP Format Wrong. Please Provide Correct Switch IP...')
        elif not _isPort(sys.argv[3]):
            print('Switch Port Format Wrong. Please Provide Correct Port Number...')
        else:
            _SW(sys.argv[2], [int(sys.argv[3])]
                ).clear_porterr_by_port(int(sys.argv[3]))

    elif sys.argv[1] == 'ptclALL':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('ptclALL'))
        elif not _checkIPlst(lstSW):
            print('IP error. Please check Switch IPs defined in Conf.ini')
        else:
            for i in range(len(lstSW)):
                _SW(lstSW[i], lstSWPorts[i]).clear_porterr_All()

    elif sys.argv[1] == 'sws':
        if len(sys.argv) != 3:
            print(strSWSHelp)
        elif not _isIP(sys.argv[2]):
            print('IP Format Wrong. Please Provide Correct Switch IP...')
        else:
            _SW(sys.argv[2], [])._switchshow()  # no ports needed

    elif sys.argv[1] == 'swsALL':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('swsALL'))
        elif not _checkIPlst(lstSW):
            print('IP error. Please check Switch IPs defined in Conf.ini')
        else:
            for i in range(len(lstSW)):
                _SW(lstSW[i], lstSWPorts[i])._switchshow()

    # save engines' 'automap.cfg', 'cm.cfg', 'san.cfg' files to local
    elif sys.argv[1] == 'bkCFG':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('bkCFG'))
        elif not _checkIPlst(lstHAAP):
            print('IP error. Please check Engine IPs defined in Conf.ini')
        else:
            strBackupFolder = '{}/{}'.format(strCFGFolder, _get_TimeNow_Folder())
            for i in lstHAAP:
                _get_HAAPInstance()[i].backup(strBackupFolder)

    # get engines' trace files under TraceFolder based on Trace levels
    elif sys.argv[1] == 'gt':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('gt'))
        elif not _checkIPlst(lstHAAP):
            print('IP error. Please check Engine IPs defined in Conf.ini')
        else:
            strTraceFolder = '{}/{}'.format(strTCFolder, _get_TimeNow_Folder())
            # for i in lstHAAP:
            #     _get_HAAPInstance()[i].get_trace(strTraceFolder, intTLevel)
            for i in range(len(lstHAAP)):
                _HAAP(lstHAAP[i]).get_trace(strTraceFolder, intTLevel)
            print('\nAll Trace Store in the Folder "%s"' % strTraceFolder)

    elif sys.argv[1] == 'anls':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('anls'))
        elif not _checkIPlst(lstHAAP):
            print('IP error. Please check Engine IPs defined in Conf.ini')
        else:
            strTraceFolder = '{}/{}'.format(strTCAFolder, _get_TimeNow_Folder())
            for i in lstHAAP:
                _get_HAAPInstance()[i].get_trace(strTraceFolder, intTLevel)
            _TraceAnalyse(strTraceFolder)

    elif sys.argv[1] == 'anlsTrace':
        if len(sys.argv) != 3:
            print(strHelpAnalyseTrace)
        elif isinstance(sys.argv[2], str):
            _TraceAnalyse(sys.argv[2])
        else:
            print('Please Provide Trace Folder To Analyse ...')

    elif sys.argv[1] == 'ec':
        if len(sys.argv) != 4:
            print(strAutoCLIHelp)
        elif not _isIP(sys.argv[2]):
            print('IP Format Wrong. Please Provide Correct Engine IP...')
        elif not _isFile(sys.argv[3]):
            print('File Not Exists. Please Provide Correct File...')
        else:
            _HAAP(sys.argv[2]).execute_multi_command(sys.argv[3])

    elif sys.argv[1] == 'pc':
        if len(sys.argv) != 3:
            print(strPCHelp)
        elif not _isIP(sys.argv[2]):
            print('IP Format Wrong. Please Provide Correct Engine IP...')
        else:
            _periodic_check(sys.argv[2])

    elif sys.argv[1] == 'pcsw':
        if len(sys.argv) != 3:
            print(strPCSWHelp)
        elif not _isIP(sys.argv[2]):
            print('IP Format Wrong. Please Provide Correct Switch IP...')
        else:
            ports = []
            for i in oddSWPort.items():
                if sys.argv[2] == i[0]:
                    ports = i[1]
            # print(ports)
            _periodic_sw_check(sys.argv[2], ports)

    elif sys.argv[1] == 'pcALL':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('pcALL'))
        elif not _checkIPlst(lstHAAP):
            print('IP error. Please check Engine IPs defined in Conf.ini')
        else:
            for i in lstHAAP:
                _periodic_check(i)

    elif sys.argv[1] == 'chgFW':
        if len(sys.argv) != 4:
            print(strHelpUpdateFW)
        elif not _isIP(sys.argv[2]):
            print('IP format wrong. Please Provide Correct Engine IP...')
        elif not _isFile(sys.argv[3]):
            print('File Not exists. Please Provide Correct File...')
        else:
            _FWUpdate(sys.argv[2], sys.argv[3])

    #     elif sys.argv[1] == 'healthHAAP':
    #         if len(sys.argv) != 2:
    #             print(strHelpSingleCommand.format('healthHAAP'))
    #         elif not _checkIPlst(lstHAAP):
    #             print('IP error. Please check Engine IPs defined in Conf.ini')
    #         else:
    #             for i in lstHAAP:
    #                 _EngineHealth(i)

    elif sys.argv[1] == 'sts':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('sts'))
        elif not _checkIPlst(lstHAAP):
            print('IP error. Please check Engine IPs defined in Conf.ini')
        else:
            _ShowEngineInfo()

    elif sys.argv[1] == 'st':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('st'))
        elif not _checkIPlst(lstHAAP):
            print('IP error. Please check Engine IPs defined in Conf.ini')
        else:
            for i in lstHAAP:
                _HAAP(i).set_time()

    elif sys.argv[1] == 'stm':
        for i in lstHAAP:
            _HAAP(i).show_engine_time()

    elif sys.argv[1] == 'wrt':
        thrd_web_rt()

    elif sys.argv[1] == 'wdb':
        thrd_web_db()

    elif sys.argv[1] == 'swc':
        for i in range(len(lstHAAP)):
            ah = _HAAP_Status(lstHAAP[i]).get_engine_AH()
            if ah == 0:
                start_warn_check()
            else:
                print('Alert Halt Exists (Engine %s)!' % lstHAAP[i])

    elif sys.argv[1] == 'test':
        
        # timing_clct_to_db(15)
        # show_N_record(3)
        pass

    elif sys.argv[1] == 'sancheck':
        if len(sys.argv) != 2:
            print(strHelpSingleCommand.format('sancheck'))
        elif not _checkIPlst(lstHAAP):
            print('IP error. Please check Engine IPs defined in Conf.ini')
        else:
            SAN_status = [{}, {}]

            for i in lstHAAP:
                _has_abts_qfull(i, SAN_status)
            # for i in lstSW:
                # _SWstatus(i,SAN_status)
    else:
        print(strHelp)


if __name__ == '__main__':
    #get_SANSW_origin()
    main()


