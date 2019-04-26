# coding:utf-8

from __future__ import print_function
import SANSW as sw
import HAAP as haap

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
        Command   Description

        ptes  : Port Error Show for SAN Switch(s)('porterrshow')
        ptcl  : Clear Port Error Counter('statsclear' or '')
        sws   : Print SAN Switch Info('switchshow')

        gt    : Get Trace of HA-AP Engine(s)
        at    : Analyse Trace of HA-AP Engine(s)
        bk    : Backup Config for HA-AP Engine(s)
        ec    : Execute Commands
        fw    : Change Firmware for HA-AP Engine
        sts   : Show Overall Status for HA-AP Engine(s)
        st    : Sync Time with Local System
        stm   : Show Time Now for HA-AP Engine(s)

        pc    : Periodically Check
        mnt   : Monitor and Show Status throgh Web Server
        '''


strPTESHelp = '''
    SAN Switch Clear Port Error Counter('statsclear' or '')
    ptes <SW_IP> | all   
        SW_IP  - for defined SAN Switch
        all    - for All SAN Switchs defined in Conf.ini
'''

strPTCLHelp = '''
    SAN Switch Port Error Show('porterrshow')
    ptcl <SW_IP Port> | all
        SW_IP Port  - for defined Port of defined SAN Switch
        all         - for All SAN Switchs defined in Conf.ini
'''

strSWSHelp = '''
    Print SAN Switch Info('switchshow')
    sws <SW_IP> | all
        SW_IP  - for defined SAN Switch
        all    - for All SAN Switchs defined in Conf.ini
'''

strGTHelp = '''
    Get Trace of HA-AP Engine(s), Save in "{trace}" Folder
    gt <HAAPIP> | all
        HAAP_IP  - for defined HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini
'''.format(trace)

strATHelp = '''
    Analyse Trace of HA-AP Engine(s)
    at <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''

strBKHelp = '''
    Backup Config for HA-AP Engine(s), Save in "{cfg}" Folder
    bk <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''.format(cfg)

strECHelp = '''
    Execute Commands listed in <Command_File> on Given Engine
    ec <HAAP_IP> <Command_File>
'''

strFWHelp = '''
    Change Firmware for Given Engine Using <FW_File>
    fw <HAAP_IP> <FW_File>
'''

strSTSHelp = '''
    sts <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''

strSTHelp = '''
    st <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''

strSTMHelp = '''
    stm <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''

strPCHelp = '''
    Periodically Check for HA-AP Engine(s) or SAN Switch(s)
    pc <sw SW_IP|haap HAAP_IP> | all
        sw SW_IP      - for Given HA-AP Engine
        haap HAAP_IP  - for Given HA-AP Engine
        all           - for All HA-AP Engines and SAN Switches        
'''

strMNTHelp = '''
    mnt real | db
        real  - for Get Status Real Time
        db   - for Get Status from DB(Need MongoDB)        
'''

# <<<Help String Field>>>


# <<<Get Config Field>>>
# Config of HAAP
HAAP_Config = gc.EngineConfig()
lstHAAP = HAAP_Config.list_engines_IP()
lstHAAPAlias = HAAP_Config.list_engines_alias()
intTNPort = HAAP_Config.telnet_port()
intFTPPort = HAAP_Config.FTP_port()
strHAAPPasswd = HAAP_Config.password()
intTraceLevel = HAAP_Config.trace_level()
# Config of SANSW
SANSW_Config = gc.SANSWConfig()
lstSANSW
lstSANSWAlias
intSWSSHPort
strSWUser
strSWPWD
dicSANSWPorts

# Config of DB



# Config of Setting

oddTraceRegular
strDesFolder
strPCFolder
lstCommand_PC_HAAP
lstCommand_PC_SANSW

refresh_interval = gc.Setting.monitor_web_refresh()

# <<<Get Config Field>>>

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


def main():
    if len(sys.argv) == 1:
        print(strHelp)

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
    main()


