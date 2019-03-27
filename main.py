# coding:utf-8

# change line 48,219,622,182
from __future__ import print_function
import ClassSW as sw
import ClassHAAP as haap
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

signal = 1
import email_form as email
#from email_form import send_warnmail

#from send_email_alltime import send_warn_mail

if signal == 0:
    email.Timely_send([1,1,1],[2,2,2])

from flask import Flask, render_template, redirect, request

try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

# <<<Help String Feild>>>
strHelp = '''
        Command           Description

        ptes           : Print Port Error of Defined SAN Switch Ports
        ptcl           : Clear Port Error Counter for Given Port on Given SAN switch
        ptclALL        : Clear Port Error Counter for All Ports on All Defined SAN switches
        sws            : Print switchshow Info for Given SAN Switch
        swsALL         : Print switchshow Info for All Defined SAN Switches
        gt             : Get Trace of All Defined Engine(s), Save in {trace} Folder
        anls           : Analyse Trace of All Defined Engine(s)
        anlsTrace      : Analyze Trace Files under <Folder>
        bkCFG          : Backup Config for All Defined Engine(s), Save in {cfg} Folder
        ec             : Execute Commands listed in <File> on Given Engine
        pc             : Execute Periodic Check on Given Engine, Save in {pc} Folder
        pcsw           : Execute Periodic Check on Given Switch, Save in {pc} Folder
        pcALL          : Execute Periodic Check on All Defined Engine(s), Save in {pc} Folder
        chgFW          : Change Firmware for Given Engine
        sts            : Show Overall Status for All Engines
        st             : Sync Time with Local System For All Engines
        stm            : Get Time of All Defined Engine(s)
        wrt            : Start Web Update Real Time
        wdb            : Start Web Update from DataBase
        sancheck       : san check
        swc            : start warning check
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

# <<<Read Config File Field>>>
objCFG = cp.ConfigParser(allow_no_value=True)
objCFG.read('Conf.ini')

# <<<DB Config>>>
strDBServer = objCFG.get('DBSetting', 'host')
intDBPort = int(objCFG.get('DBSetting', 'port'))
strDBName = objCFG.get('DBSetting', 'name')
# <<<DB Config>>>

# <<<SAN Switch Config>>>
strSWUser = objCFG.get('SWSetting', 'username')
intSWSSHPort = int(objCFG.get('SWSetting', 'port'))

oddSWPort = Odd()
for i in objCFG.items('SWPorts'):
    oddSWPort[i[0]] = eval(i[1])
    # print(oddSWPort)
# print(oddSWPort)
# for i in oddSWPort.items():
    # print(type(i)) 
    

lstSW = list(oddSWPort.keys())
lstSWPorts = list(oddSWPort.values())
# print(oddSWPort)

# if i == '172.16.254.75':
# print (oddSWPort.values())
# print (lstSWPorts,lstSW,)

strSWPWD = objCFG.get('SWSetting', 'password')
if strSWPWD:
    strSWPWD = strSWPWD
else:
    strSWPWD = getpass.getpass(
        prompt='Please Input Your SAN Switch Password for User {}:'.format(
            strSWUser), stream=None)
# <<<SAN Switch Config>>>

# 获取交换机的Ip
# <<<SAN Switch Config>>>
addSwitches = Odd()
for i in objCFG.items('Switches'):
    addSwitches[i[0]] = i[1]
lstSwitchAlias = list(addSwitches.keys())
lstSwitch = list(addSwitches.values())

# <<<HAAP Config>>>
oddEngines = Odd()
for i in objCFG.items('Engines'):
    oddEngines[i[0]] = i[1]
lstHAAPAlias = list(oddEngines.keys())
lstHAAP = list(oddEngines.values())
# lstHAAP = list(i[0] for i in objCFG.items('Engines'))
intTLevel = int(objCFG.get('MessageLogging', 'TraceLevel'))
intTNPort = int(objCFG.get('EngineSetting', 'TelnetPort'))
intFTPPort = int(objCFG.get('EngineSetting', 'FTPPort'))
lstCheckCMD = list(i[0] for i in objCFG.items('PeriodicCheckCommand'))
# lstSWCheckCMD = list(i[0] for i in objCFG.items('PeriodicSWCheckCommand'))

strHAAPPasswd = objCFG.get('EngineSetting', 'HAAPPassword')
if strHAAPPasswd:
    strHAAPPasswd = strHAAPPasswd
else:
    strHAAPPasswd = getpass.getpass(
        prompt='Please Input Your Engine Password: ', stream=None)

oddHAAPErrorDict = Odd()
for i in objCFG.items('TraceRegular'):
    oddHAAPErrorDict[i[0]] = eval(i[1])

# <<<HAAP Config>>>

# <<<Folder Config>>>
# SWPEFolder = SAN Switch Port Error Folder
strSWPEFolder = objCFG.get('FolderSetting', 'swporterr')
# TCFolder = HAAP Get Trace Folder
strTCFolder = objCFG.get('FolderSetting', 'trace')

# TCAFolder = HAAP Trace Analyse Folder
strTCAFolder = objCFG.get('FolderSetting', 'traceanalyse')
# CFGFolder = HAAP Config Backup Folder
strCFGFolder = objCFG.get('FolderSetting', 'cfgbackup')
# PCFolder = HAAP Periodic Check Result Folder
strPCFolder = objCFG.get('FolderSetting', 'PeriodicCheck')

# <<<Folder Config>>>
# <<<Read Config File Field>>>

# <<<Inside Function Feild>>>

# <<<warn level>>>
level1 = objCFG.get('level', '1')
level1 = eval(level1)
abtslv1 = level1['abts']
qflv1 = level1['Q_full']
eclv1 = level1['Encout']
d3lv1 = level1['Discc3']

level2 = objCFG.get('level', '2')
level2 = eval(level2)
abtslv2 = level2['abts']
qflv2 = level2['Q_full']
eclv2 = level2['Encout']
d3lv2 = level2['Discc3']

level3 = objCFG.get('level', '3')
level3 = eval(level3)
abtslv3 = level3['abts']
qflv3 = level3['Q_full']
eclv3 = level3['Encout']
d3lv3 = level3['Discc3']
# print(type(abtslv1))

# ################################################

# <<<refreshtime Config>>>

flashfreshtime = objCFG.get('Refreshtime', 'flashfreshtime')
databasefreshtime = objCFG.get('Refreshtime', 'databasefreshtime')
timeup = flashfreshtime
databasefresh = int(databasefreshtime,)
# <<<refreshtime Config>>>

#<<<2h用户未确认邮件发送>>>
sub= "用户未确认信息"
mailto_list = objCFG.get('EmailSetting','receiver')
#<<<2h用户未确认邮件发送>>>


def _get_TimeNow_Human():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _get_TimeNow_Folder():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


# en-Instance The HAAP by IP...
def _HAAP(strEngineIP):
    return haap.HAAP(strEngineIP, intTNPort, strHAAPPasswd, intFTPPort)


def _HAAP_Status(strEngineIP):
    return haap.HAAP_Status(strEngineIP, intTNPort, strHAAPPasswd, intFTPPort)


# en-Instance The SAN Switch by IP and SAN Switch Ports...
def _SW(strSWIP, lstSWPorts):
    return sw.SANSW(strSWIP, intSWSSHPort,
                    strSWUser, strSWPWD, lstSWPorts)


# en-Instance All The SAN Switchs by IP and SAN Switch Ports...
def _get_SWInstance():
    oddSWInst = Odd()
    for i in range(len(lstSW)):
        oddSWInst[lstSW[i]] = sw.SANSW(lstSW[i], intSWSSHPort,
                                       strSWUser, strSWPWD, lstSWPorts[i])
    return oddSWInst

    # print ('aaaaaa:'),oddSWInst


def _sw_switchshow(strSWIP):
    _SW(strSWIP, [])._switchshow()

# en-Instance ALL The HAAPs in the config file by IP...


def _get_HAAPInstance():
    oddTNInst = Odd()
    for i in range(len(lstHAAP)):
        oddTNInst[lstHAAP[i]] = _HAAP_Status(lstHAAP[i])
        # print('aaaaaa:'), lstHAAP
    return oddTNInst

# analyze trace files under DesFolder, results saved in .xsl files


def _TraceAnalyse(strDesFolder):
    s.TraceAnalyse(oddHAAPErrorDict, strDesFolder)

# execute periodic-check commands (defined in Config.ini),\
# print and save results in PCFolder


def _periodic_check(strEngineIP):
    _HAAP(strEngineIP).periodic_check(lstCheckCMD,
                                      strPCFolder,
                                      'PC_{}_{}.log'.format(
                                          _get_TimeNow_Folder(), strEngineIP))


def _periodic_sw_check(strSWIP, ports):
    # lstSWport = 0
    cmd = 'portshow '
    lstSWCheckCMD = ['switchshow', 'porterrorshow']
    # lstSWCheckCMD.insert('aaa1')
    for i in ports:
        i = str(i)
        #print(i, type(i))
        cmd += i
        #print(cmd)
        lstSWCheckCMD.insert(-1, cmd)
        cmd = 'portshow '
    #print(lstSWCheckCMD)
    _SW(strSWIP, lstSWPorts).periodic_sw_check(lstSWCheckCMD,
                                               strPCFolder,
                                               'PC_{}_{}.log'.format(
                                                   _get_TimeNow_Folder(), strSWIP))


def _has_abts_qfull(strEngineIP, SANstatus):
    _HAAP(strEngineIP).has_abts_qfull(SANstatus, strEngineIP)


def _SWstatus(strSWIP, SANstatus):
    _SW(strSWIP, lstSWPorts).SWstatus(strSWIP, SANstatus)


# execute cmds in file and print the results
def _AutoCLI(strEngineIP, CMDFile):
    _HAAP(strEngineIP).execute_multi_command(CMDFile)


def _FWUpdate(strEngineIP, strFWFile):
    _HAAP(strEngineIP).updateFW(strFWFile)


def _EngineHealth(strEngineIP):
    alert = _HAAP(strEngineIP).get_engine_health()
    if alert is not None:
        if alert:
            al_st = "AH"
        else:
            al_st = "OK"
        #print("{}: {}".format(strEngineIP, al_st))

# def _ShowEngineInfo(strEngineIP):
#     engineIns = _HAAP(strEngineIP)
#     print "{:<17s}:".format("Engine IP"), strEngineIP
#     print "{:<17s}:".format("Status"), engineIns.get_engine_status()
#     print "{:<17s}:".format("Firmware version"), engineIns.get_version()
#     print "{:<17s}:".format("Uptime"), engineIns.get_uptime()
#
#     if engineIns.get_engine_health():
#         print "{:<17s}: AH".format("Alert Halt")
#     else:
#         print "{:<17s}: None".format("Alert Halt")
#
#     if engineIns.is_master_engine():
#         print "{:<17s}: Yes".format("Master")
#     else:
#         print "{:<17s}: No".format("Master")
#
#     mirror_status = engineIns.get_mirror_status()
#     if mirror_status == 0:
#         print "{:<17s}: All OK\n".format("Mirror status")
#     else:
#         print "{:<17s}: \n".format("Mirror status"), mirror_status, "\n"


def _ShowEngineInfo():
    dictEngines = _get_HAAPInstance()
    info_lst = []
    for i in lstHAAP:
        info_lst.append(dictEngines[i].infoEngine_lst()[0])

    def general_info():
        lstDesc = ('EngineIP', 'Uptime', 'AH', 'Firm_Version',
                   'Status', 'Master', 'Mirror', 'ABTs', 'Qfull')
        for strDesc in lstDesc:
            print(strDesc.center(14), end=''),
        print()
        for i in info_lst:
            for s in i:
                if s is not None:
                    print(s.center(14), end=''),
                else:
                    print("None".center(14), end=''),
            print()

    def mirror_info():  # needs optimization
        print("\nMirror Error")
        for i in lstHAAP:
            print(i, ":")
            mirror_status = dictEngines[i].get_mirror_status()
            if mirror_status != 0 and mirror_status != -1:
                print(mirror_status)
            else:
                print("None")

    general_info()
    mirror_info()


def _isIP(s):
    p = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(s):
        return True
    else:
        return False


def _checkIPlst(lstIP):
    return all(map(_isIP, lstIP))


def _isFile(s):
    if os.path.isfile(s):
        return True
    else:
        return False


def _isPort(s):
    if type(s) == int:
        return True
    if type(s) == str:
        if s.isdigit():
            if type(eval(s)) == int:
                return True
    return False


# by klay
def get_HAAP_status_list():

    try:
        db = DB_collHAAP()
        last_update = db.get_last_record()
        #print(last_update[1])
        xxx = last_update[1]
        #print(xxx)
    except:
        print('get_HAAP_status_list')
    lstHAAPstatus = []
    warnlist = []
    warnlevel = []
    for i in range(len(lstHAAP)):
        # print('kkkkkkkk')
        #print(xxx[i])
        #print(i)
        #print(lstHAAPAlias)
        t = {}
        t[lstHAAPAlias[i]] = _HAAP_Status(lstHAAP[i]).infoEngine_lst()[1]
        lstHAAPstatus.append(t)
        #print('lstHAAPstatus',t)
        try:
            items_db = xxx[i].values()[0]
        except:
            pass
        for items in t.values():

            #print(items)
            #print(xxx[i])
            eglevel = 0
            # print(items['Status'])
            if items['Status'] == 'ONLINE':
                try:
                    if items_db['Status'] == 'ONLINE':  # xxx is engine status from DB's first record
                        #print('okokok')
                        warnlist.append('Engine' + lstHAAP[i] + '\'s status is ' + items['Status'])
                        warnlevel.append('3')
                except:
                    pass
            if items['Mirror'] == 'All OK':
                try:
                    if items_db['Mirror'] == 'All OK':  # xxx is engine status from DB's first record
                        warnlist.append('Engine' + lstHAAP[i] + '\'s mirror is ' + 'not ok')
                        warnlevel.append('3')
                except:
                    pass
            s = 0
            s1 = 0
            uptime = items['Uptime']
            #print ('uptime',uptime)
            s += int(uptime[-2:])
            s += int(uptime[-5:-3]) * 60
            s += int(uptime[-8:-6]) * 3600
            if 'd' in uptime:
                patt = re.compile(r'(\d*)')
                day = patt.match(uptime).group()
                s += int(day) * 24 * 60 * 60
            try:
                uptime1 = items_db['Uptime']
                s1 += int(uptime1[-2:])
                s1 += int(uptime1[-5:-3]) * 60
                s1 += int(uptime1[-8:-6]) * 3600
                if 'd' in uptime1:
                    patt = re.compile(r'(\d*)')
                    day = patt.match(uptime1).group()
                    s1 += int(day) * 24 * 60 * 60
                if uptime1 < uptime:
                    warnlist.append('Engine' + lstHAAP[i] + ' had reboot')
                    warnlevel.append('2')
            except:
                pass
                # print(warnlist)
            #if warnlist != []:
                #emailSend_warnmail(warnlist,warnlevel)
    #print('dsd',lstHAAPstatus,warnlist,warnlevel)
    # return lstHAAPstatus
    # if warnlist != []:
    #     #print(warnlist)
    #     #print(type(warnlist))
    #     print('send..................')
    #     email.Timely_send(warnlist,warnlevel)
    return [lstHAAPstatus, warnlist, warnlevel]

###########################分割线##################################################
'''
@author: Paul
@note: 交换机数据库数据获取

'''
# --SwitchIP---#


def get_Switch_IP():
    lstsw_ip = {}
    a = lstSwitchAlias
    b = lstSwitch
    lstsw_ip = dict(zip(a, b))
   # print("lstsw_ip:",lstsw_ip)
    return lstsw_ip


# --Switch端口总数--#
def get_Switch_status_list():
    lstSwitchstatus = {}
    for i in range(len(lstSW)): 
        a = {}
        for h in range(len(lstSWPorts[i])):
            q = lstSWPorts[i][h]
            b = _SW(lstSW[i], lstSWPorts[i])._dicPartPortError[q]            
            a['port' + str(lstSWPorts[i][h])] = b
        lstSwitchstatus['Switch' + str(i)] = (a) 
        # print ("lstSwitchstatus:", lstSwitchstatus)
    return lstSwitchstatus


# --错误总数--#
def get_Switch_Total():

    try:
        db = DB_collHAAP()
        last_update = db.get_last_record_Switch()
        lstStatusdict = last_update[3]
        #print(lstStatusdict)

    except:
        pass
    
    lst_total = {}
    sw_warnlist = []
    sw_warnlevel = []
    
    for i in range(len(lstSW)): 
        lstSwitchstatus = {}
        FramTX = []
        FramRX = []
        ENCOUT = []
        Discc3 = []
        LinkFL = []
        LossSC = []
        LossSG = []
        ALLTOTAL = []
        ALLTOTAL_change = []
        
        ALLtotal = 0
        ALLtotal_change = 0
        
        framtx = 0
        framrx = 0 
        encout = 0
        discc3 = 0
        linkfl = 0
        losssc = 0
        losssg = 0
        a = {}
        for h in range(len(lstSWPorts[i])):
            q = lstSWPorts[i][h]
            b = _SW(lstSW[i], lstSWPorts[i])._dicPartPortError[q]
           # print("b:", b)
            if b[0][-1] == 'm' or b[0][-1] == 'k':
                if b[0][-1] == 'm':
                    b[0] = (float(b[0][0:-1])) * 10000
                else:
                    b[0] = (float(b[0][0:-1])) * 1000
            framtx += int(b[0])
            # print("framtx:",framrx)
            if b[1][-1] == 'm' or b[1][-1] == 'k':
                if b[1][-1] == 'm':
                    b[1] = (float(b[1][0:-1])) * 10000
                else:
                    b[1] = (float(b[1][0:-1])) * 1000
            framrx += int(b[1])
            if b[2][-1] == 'm' or b[2][-1] == 'k':
                if b[2][-1] == 'm':
                    b[2] = (float(b[2][0:-1])) * 10000
                else:
                    b[2] = (float(b[2][0:-1])) * 1000
            encout += int(b[2])
            if b[3][-1] == 'm' or b[3][-1] == 'k':
                if b[3][-1] == 'm':
                    b[3] = (float(b[3][0:-1])) * 10000
                else:
                    b[3] = (float(b[3][0:-1])) * 1000
            discc3 += int(b[3])
            if b[4][-1] == 'm' or b[4][-1] == 'k':
                if b[4][-1] == 'm':
                    b[4] = (float(b[4][0:-1])) * 10000
                else:
                    b[4] = (float(b[4][0:-1])) * 1000
            linkfl += int(b[4])
            if b[5][-1] == 'm' or b[5][-1] == 'k':
                if b[5][-1] == 'm':
                    b[5] = (float(b[5][0:-1])) * 10000
                else:
                    b[5] = (float(b[5][0:-1])) * 1000
            losssc += int(b[5])
            if b[6][-1] == 'm' or b[6][-1] == 'k':
                if b[6][-1] == 'm':
                    b[6] = (float(b[6][0:-1])) * 10000
                else:
                    b[6] = (float(b[6][0:-1])) * 1000
            losssg += int(b[6])
            
            ALLtotal = encout + discc3 + linkfl + losssc + losssg
                    
            # print("losssg:", losssg) 
            # s = str(lstSW[i]) + ':' + ' '
            s = str(framtx)
            # s2 = str(lstSW[i]) + ':' + ' '
            s1 = str(framrx)
            s2 = str(encout)
            s3 = str(discc3)
            s4 = str(linkfl)
            s5 = str(losssc)
            s6 = str(losssg)
            s7 = str(ALLtotal)

            FramTX.append(s)
            FramRX.append(s1)
            ENCOUT.append(s2)
            Discc3.append(s3)
            LinkFL.append(s4)
            LossSC.append(s5)
            LossSG.append(s6)
            ALLTOTAL.append(s7)
         
            #lstSwitchstatus.update(FramTX=framtx)
            #lstSwitchstatus.update(FramRX=framrx)
            lstSwitchstatus.update(ENCOUT=encout)
            lstSwitchstatus.update(Discc3=discc3)
            lstSwitchstatus.update(LinkFL=linkfl)
            lstSwitchstatus.update(LossSC=losssc)
            lstSwitchstatus.update(LossSG=losssg)
            lstSwitchstatus.update(ALLTOTAL=ALLtotal)

        switchname = objCFG.options("Switches")
        # print ('switch_name',switchname)
        sname = switchname[i]

        #print("sname:",sname)
           
        lst_total[sname] = (lstSwitchstatus)
        #print('lst_total[sname]',lst_total[sname])

        # print(i,'   sd  ',Alltotal)
        
        try:
            a = lstStatusdict[sname]
            #print("123131313:",a)
            #print ('count ', ALLTOTAL)
            # print('2222')
            # 运行不到
            #print('333333', a['ALLTOTAL'])

            a = ALLtotal - a['ALLTOTAL']

            #print("axxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:", a)
            if a == 0:
                #print('aaaaaa=======000000')
                # sw_warnlist.append('llllllllllll')
                #print('4444444444')
                #print("a:", a)
                #print("sdsdsdswwww:", 'Switch' + lstSW[i] + '\' s port error has reached ' + str(a))
                sw_warnlist.append('Switch' + lstSW[i] + '\' s port error has reached ')
                #print('hgjhsgdjhsgjhsgfjhsdgfjs')
                sw_warnlevel.append('3')
                #print('                    ', sw_warnlevel, sw_warnlist)

            else:
                if a > 10000:
                    sw_warnlist.append('Switch' + lstSW[i] + '\'s port error has reached ' + str(a))
                    sw_warnlevel.append('2')
                else:
                    if a > 5000:
                        sw_warnlist.append('Switch' + lstSW[i] + '\'s port error has reached '+str(a))
                        sw_warnlevel.append('1')
        except:
            pass 


            #print("lstSwitchstatus:", lst_total, " ",sw_warnlist," ",sw_warnlevel)
            
    # if warnlist != []:
    #     #print(warnlist)
    #     #print(type(warnlist))
    #     email.Timely_send(sw_warnlist,sw_warnlevel)
    return lst_total, sw_warnlist, sw_warnlevel

################################分割线######################################################


'''
def email_send():
    email_info = []
    
    enginelist = engine_info[0]
    switch_info = get_Switch_Total()
    sw_warnlist = switch_info[1]
    sw_warnlevel = switch_info[0]
    if enginelist !=[]:
        email_info.update(enginelist(i))
        email_info.append(enginelevel(i))
    else:
        email_info.append(sw_warnlist(i))
        email_info.append( sw_warnlevel(i))
    print('dfsds', email_info)
    print('dfsd', enginelist)

'''
'''
def email_send_engine():
    engine_info = get_HAAP_status_list()
    print ('engine_info',engine_info)
    enginelevel= engine_info[2]
    time = _get_TimeNow_Human()
    for g in enginelevel:
        pass




    warninfo = send_warn_mail(mailto_list, sub,)
    print('ddf',warninfo)
    return warninfo

'''





class collHAAP(Document):
    time = DateTimeField(default=datetime.datetime.now())
    engine_status = ListField()


class collWARN(Document):
    time = DateTimeField(default=datetime.datetime.now())
    level = StringField()
    warn_message = StringField()
    confirm_status = IntField()


# by wen
class collSWITCH(Document):
    time = DateTimeField(default=datetime.datetime.now())
    Switch_ip = DictField()
    Switch_status = DictField()
    Switch_total = DictField()


class DB_collHAAP(object):
    connect(strDBName, host=strDBServer, port=intDBPort)

    def haap_insert(self, time_now, lstSTS):
        t = collHAAP(time=time_now, engine_status=lstSTS)
        t.save()

    def haap2_insert(self, time_now, lstdj, lstSTS, confirm):
        t = collWARN(time=time_now, level=lstdj, warn_message=lstSTS, confirm_status=confirm)
        t.save()

#BY wen###
    def Switch_insert(self, time_now, lstSW_IP, lstSWS, lstSW_Total):
        t = collSWITCH(time=time_now, Switch_ip=lstSW_IP, Switch_status=lstSWS, Switch_total=lstSW_Total)
        t.save()

    def haap_query(self, time_start, time_end):
        collHAAP.objects(date__gte=time_start,
                         date__lt=time_end).order_by('-date')

    def haap_list_all(self):
        for i in collHAAP.objects().order_by('-time'):
            print(i.time, i.engine_status)

    def get_N_record_in_list(self, intN):
        N_record = collHAAP.objects().order_by('-time').limit(intN)
        lstRecord = []
        for x in range(len(N_record)):
            lstRecord.append([])
            lstRecord[x].append(N_record[x].time)
            for i in range(len(N_record[x].engine_status)):
                for k in N_record[x].engine_status[i].keys():
                    lstRecord[x].append(N_record[x].engine_status[i][k])
        return lstRecord

    def show_N_record(self, intN):
        r = self.get_N_record_in_list(intN)
        tuplDesc = ('Engine', 'Uptime', 'AH', 'FirmWare',
                    'Status', 'Master', 'Mirror')
        tuplWidth = (18, 16, 7, 13, 9, 9, 12)
        for i in r:
            print('\n Time: %s\n' % str(i[0]))
            w = i[1:]
            for d in range(len(tuplDesc)):
                print(tuplDesc[d].ljust(tuplWidth[d]), end='')
            print()
            for p in w:
                for x in range(len(p)):
                    print(p[x].ljust(tuplWidth[x]), end='')
                print()

    def get_last_record(self):
        last_record = collHAAP.objects().order_by('-time').first()
        return (last_record.time, last_record.engine_status)
    
#######By Wen#######
    def get_last_record_Switch(self):
        last_record = collSWITCH.objects().order_by('-time').first()
        return(last_record.time, last_record.Switch_ip, last_record.Switch_status, last_record.Switch_total)

# By Zane
    def get_recond(self):
        warns = []
        a = collWARN.objects(confirm_status = 0)
        for z in a:
            warns.append({'level':z.level,'time':z.time,'message':z.warn_message})
        return(warns)

    def upconfirm(self):
        upconfirm = collWARN.objects(confirm_status = 0).update(confirm_status = 1)
     
# By Zane
def get_all_recond():
    db = DB_collHAAP()
    last_update = db.get_recond()
    #print(last_update)
    return last_update

def upconfirm_stuta():
    db = DB_collHAAP()
    db.upconfirm()

# By Zane
def get_engine_from_db():
    db = DB_collHAAP()
    last_update = db.get_last_record()
    
    refresh_time = last_update[0]
    lstStatusDict = last_update[1]
    #print("A",lstStatusDict)
    lstStatus = []
    #print('B',lstHAAPAlias)
    for i in lstStatusDict:
        a = i.values()[0]
        #print(a)
        b = [a['IP'],a['Status'],a['Uptime'],a['Master'],a['Mirror']]
        lstStatus.append(b)
    #print('C',lstStatus)
    #print("999999999")
    return refresh_time, lstStatus


# By Zane
def get_Switch_from_db():
    db = DB_collHAAP()
    last_update = db.get_last_record_Switch()
    refresh_time = last_update[0]
    lstSwitch_ip = last_update[1]
    lstSwitch_status = last_update[2]
    lstSwitch_total = last_update[3]
    
    # print(lstSwitch_total)
    '''lstSwitch_totals = []
    for i in lstSwitch_total:
        lstswitch_totals = [lstSwitch_ip[i]]
        for o in lstSwitch_total[i]:
            if o == "ALLTOTAL":
                continue
            else:
                lstswitch_totals.append(lstSwitch_total[i][o])
        lstswitch_totals.append(lstSwitch_total[i]["ALLTOTAL"])
        lstSwitch_totals.append(lstswitch_totals)'''

    lstall = [refresh_time,lstSwitch_ip,lstSwitch_status,lstSwitch_total]
    #print("lstall:",lstall)
    return lstall




def start_web(mode):
    app = Flask(__name__, template_folder='./web/templates',
                static_folder='./web/static', static_url_path='')

    @app.route("/", methods=['GET', 'POST'])
    def home():
        lstDesc = ('EngineIP', 'Status', 'Uptime', 'Master', 'Mirror')
        lstDesc_switches = ('SwitchIP', 'Encout', 'Discc3', 'Link fail', 'Loss sigle', 'Loss sync')
    
        # swich的IP地址
        Switches_ip = []
        for ip in objCFG.options("Switches"):
            Switches_ip.append(objCFG.get("Switches",(ip)))

        if mode == 'rt':
            refresh_time = _get_TimeNow_Human()
            Status = []
            dictEngines = get_HAAP_status_list()
            for i in range(len(lstHAAPAlias)):
                Status.append(dictEngines[i][lstHAAPAlias[i]])

        elif mode == 'db':
            tuplHAAP = get_engine_from_db()
            tuplSWITCH = get_Switch_from_db()
            
            if tuplHAAP:
                engine_refresh_time = tuplHAAP[0]
                Status = tuplHAAP[1]
            else:
                engine_refresh_time = _get_TimeNow_Human()
                Status = None
                
            if tuplSWITCH:
                switch_refresh_time = tuplSWITCH[0]
                Status_Switch = tuplSWITCH[3]
                Status_switch = []
                for i in Status_Switch:
                    total = []
                    total.append(objCFG.get("Switches",(i)))
                    total.append(Status_Switch[i]['ENCOUT'])
                    total.append(Status_Switch[i]['Discc3'])
                    total.append(Status_Switch[i]['LinkFL'])
                    total.append(Status_Switch[i]['LossSG'])
                    total.append(Status_Switch[i]['LossSC'])
                    Status_switch.append(total)
            else:
                switch_refresh_time = _get_TimeNow_Human()
                Status_Switch = None

        # 未确认错误信息
        error_message = get_all_recond()
        warns = {}
        try:
            for i in Status:
                warns[i[0]] = 1
            for i in Status_switch:
                warns[i[0]] = 1
            for i in error_message:
                for j in warns:
                    if j in i['message'] and warns[j] < int(i['level']):
                        warns[j] = int(i['level'])
                    else:
                        pass
        except:
            pass

        # 预警提示弹出为0，不弹出为1
        if request.method == 'GET' and error_message:
            error = 1
        else:
            upconfirm_stuta()
            error = 0

        # 刷新时间
        timeup=5
        
        return render_template("monitor.html",
                               Title = lstDesc,
                               Title_switches = lstDesc_switches,
                               engine_refresh_time = engine_refresh_time,
                               switch_refresh_time = switch_refresh_time,
                               Status = Status,
                               Status_switch = Status_switch,
                               Switches_ip = Switches_ip,
                               timeup = timeup,
                               error = error,
                               error_message = error_message,
                               warns = warns)

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


def job_update_interval2(intInterval):
    t = s.Timing()
    db = DB_collHAAP()

    def do_it():
        n = datetime.datetime.now()
        #print(get_HAAP_status_list()[2])

        a = get_HAAP_status_list()
        #do_update = db.haap_insert(n, a[0])
        db.haap_insert(n, a[0])
        if a[2] != []:
            for i in range(len(a[2])):

                #do_update = db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                # print('update complately...@ %s' % n)
            warnlist = a[1]
            warnlevel = a[2]
            email.Timely_send(warnlist, warnlevel)

    t.add_interval(do_it, 10)
    t.stt()


# #线程3交换机的
def job_update_interval3(intInterval):
    t = s.Timing()
    db = DB_collHAAP()

    def do_it():
        n = datetime.datetime.now()
        a = get_Switch_Total()
        #do_update_Switch = db.Switch_insert(n, get_Switch_IP(), get_Switch_status_list(), a[0])
        db.Switch_insert(n, get_Switch_IP(), get_Switch_status_list(), a[0])
        if a[1] != []:
            for i in range(len(a[2])):
                #do_update = db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                db.haap2_insert(n, a[2][i], a[1][i], confirm_status)
                # print('update complately...@ %s' % n)
                #return do_update_Switch, do_update
            warnlist = a[1]
            warnlevel = a[2]
            email.Timely_send(warnlist, warnlevel)

    t.add_interval(do_it, 600)
    t.stt()

# def DB_Update_interval(intSec):
#     t = s.Timing()
#     db = DB_collHAAP()
#     def job_update_interval():
#         do_update = db.haap_insert(get_HAAP_status_list())
#         print('update complately...@ %s' % datetime.datetime.now())
#         return do_update

#     t.add_interval(job_update_interval, intSec)
#     t.stt()




#线程4发送邮件
def job_update_interval4(intInterval):
    t = s.Timing()
    db = DB_collHAAP()
    def do_it():
        warninfo = email.send_warnmail(mailto_list, sub,get_all_recond())
        #print('ddf',warninfo)
        return warninfo
    t.add_interval(do_it, intInterval)
    t.stt()


#线程4发送邮件

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

'''
def thrd_web_db():
    t1 = Thread(target=start_web, args=('db',))
    t2 = Thread(target=job_update_interval, args=(10,))

    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    try:
        while t2.isAlive():
            pass
        while t1.isAlive():
            pass
    except KeyboardInterrupt:
        stopping_web(3)
'''

# by klay
def start_warn_check():
    t1 = Thread(target=start_web, args=('db',))
    t2 = Thread(target=job_update_interval2, args=(10,))
    t3 = Thread(target=job_update_interval3, args=(600,))
    t4 = Thread(target=job_update_interval4, args=(20*360,))

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

# #<<<Warning Collection>>>
# def get_wc():
#     lstwarnstatus = []
#     eglevel = 0
#     aslv = 0
#     qlv = 0
#     lvlist=[]
#     #<<get engine warning status>>
#     for i in range(len(lstHAAP)):
#         s = 'Engine'
#         #s += lstHAAP[i]
#         t = {}
#         t[s] = _HAAP_Status(lstHAAP[i]).get_egw()#engine warning status
#         #t.update({'Ip':i})
#         for items in t.values():
#             for k,v in items.items():#for key,value in dict
#                 if v == 0:
#                     items.pop(k)
#         print(t)
#         print(t.values()[0])
#         if t.values() != [{}]:
#             a = t.values()[0]
#             print('aaaaa',a)
#             #print(type(a))
#             for k, v in a.items():
#                 if k == 'Reboot':
#                     eglevel = 3
#                     lvlist.append(eglevel)
#                 elif k == 'Mirror':
#                     eglevel =3
#                     lvlist.append(eglevel)
#                 elif k == 'ABTs':
#                     if v > abtslv3: aslv = 3
#                     elif v > abtslv2: aslv = 2
#                     else : aslv =1
#                     lvlist.append(aslv)
#
#
#                 else:
#                     if k == 'Qfull':
#                         if v > qflv3:
#                             qlv = 3
#                         elif v > qflv2:
#                             qlv = 2
#                         else:
#                             qlv = 1
#                         lvlist.append(qlv)
#
#
#
#
#
#
#             lstwarnstatus.append(t)
#         print(eglevel,lvlist)
#     eglevel = max(lvlist)
#     print(eglevel)

        # print(lstwarnstatus)

    # pass


# <<<Warning Collection>>>
def get_wc():
    lstwarnstatus = []
    eglevel = 0
    aslv = 0
    qlv = 0
    lvlist = []
    # <<get engine warning status>>
    for i in range(len(lstHAAP)):
        s = 'Engine'
        # s += lstHAAP[i]
        t = {}
        t[s] = _HAAP_Status(lstHAAP[i]).get_egw()  # engine warning status
        # t.update({'Ip':i})
        for items in t.values():
            for k, v in items.items():  # for key,value in dict
                if v == 0:
                    items.pop(k)
        #print(t)
        #print(t.values()[0])
        if t.values() != [{}]:
            a = t.values()[0]
           #print('aaaaa', a)
            # print(type(a))
            for k, v in a.items():
                if k == 'Reboot':
                    eglevel = 3
                    lvlist.append(eglevel)
                elif k == 'Mirror':
                    eglevel = 3
                    lvlist.append(eglevel)
                elif k == 'ABTs':
                    if v > abtslv3: aslv = 3
                    elif v > abtslv2: aslv = 2
                    else : aslv = 1
                    lvlist.append(aslv)

                else:
                    if k == 'Qfull':
                        if v > qflv3:
                            qlv = 3
                        elif v > qflv2:
                            qlv = 2
                        else:
                            qlv = 1
                        lvlist.append(qlv)

            lstwarnstatus.append(t)
        #print(eglevel, lvlist)
    eglevel = max(lvlist)
    #print(eglevel)


def wc_tdb():
    pass


def check_warn():
    get_wc()
    pass

# ################################################
# <<<Inside Function Field>>>


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
        start_warn_check()

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
    #get_engine_from_db()
    #get_HAAP_status_list()
    #get_all_recond()sb
    #get_Switch_from_db()
    #get_Switch_Total()
    #get_HAAP_status_list()
    main()
    #email_send()
    #job_update_interva(10,)
    #job_update_interval4(10,)P't't
    #start_web('db')
    #get_all_recond()