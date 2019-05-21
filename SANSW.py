# coding: utf-8
from __future__ import print_function
from ClassConnect import *
from collections import OrderedDict as odd
import re
import Source as s
import os
import time
import GetConfig as gc
import array
from functools import total_ordering
objSwitchConfig = gc.SwitchConfig()

# <<<Get Config Field>>>
swcfg = gc.SwitchConfig()
list_sw_IP = swcfg.list_switch_IP()
list_sw_alias = swcfg.list_switch_alias()
ssh_port = swcfg.SSH_port()
user = swcfg.username()
passwd = swcfg.password()
list_sw_ports = swcfg.list_switch_ports()
tuplThresholdTotal = swcfg.threshold_total()

setting = gc.Setting()
lstPCCommand = setting.PCEngineCommand()
strPCFolder = setting.folder_PeriodicCheck()
sw_ID=swcfg.list_switch_alias()
level_sw=swcfg.threshold_total()
# <<<Get Config Field>>>

def clear_all():
    for ip in list_sw_IP:
        Action(ip, ssh_port, user, passwd, []).clear_all_port()

def clear_one_port(ip, sw_port):
    Action(ip, ssh_port, user, passwd, []).clear_one_port(sw_port)

# def print_porterror_all():
#     for ip in list_sw_ip:
#         Action(ip, ssh_port, user, passwd, []).print_porterrshow()

# def print_porterror(ip):
#     Action(ip, ssh_port, user, passwd, []).print_porterrshow()

def print_porterror_all_formated():
    for i in range(len(list_sw_IP)):
        Status(list_sw_IP[i],
                ssh_port,
                user,
                passwd,
                list_sw_ports[i]).print_porterror_formated()

def print_porterror_formated(ip):
    def get_index(ip, list_sw_IP):
        if ip in list_sw_IP:
            return list_sw_IP.index(ip)
        else:
            print('"%s" is NOT Configured in Conf.ini' % ip)
    id = get_index(ip, list_sw_IP)
    if id is not None:
        Status(list_sw_IP[id],
         ssh_port,
          user,
           passwd,
            list_sw_ports[id]).print_porterror_formated()


def print_switchshow_all():
    for ip in list_sw_IP:
        Action(ip, ssh_port, user, passwd, []).print_switchshow()

def print_switchshow(ip):
    if ip in list_sw_IP:
        Action(ip, ssh_port, user, passwd, []).print_switchshow()
    else:
        print('"%s" is NOT Configured in Conf.ini' % ip)

def periodically_check_all():
    for ip in list_sw_IP:
        PCFile_name = 'PC_%s_Engine_%s.log' % (
            s.time_now_folder(), ip)
        Action(ip, ssh_port, user, passwd, []).periodic_check(
            lstPCCommand, strPCFolder, PCFile_name)

def periodically_check(ip):
    PCFile_name = 'PC_%s_Engine_%s.log' % (
        s.time_now_folder(), ip)
    Action(ip, ssh_port, user, passwd, []).periodic_check(
        lstPCCommand, strPCFolder, PCFile_name)


class Action():

    def __init__(self, strIP, intPort, strUserName, strPasswd,
                 lstSWPort, intTimeout=2):
        self._host = strIP
        self._port = intPort
        self._username = strUserName
        self._password = strPasswd
        self._timeout = intTimeout
        self._allSWPort = lstSWPort
        self.strPorterrshow = None
        self.strSwitchshow = None
        self._SWConn = None
        self._get_switch_info()


    @s.deco_Exception
    def _get_switch_info(self):
        try:
            self._SWConn = SSHConn(self._host,
                                   self._port,
                                   self._username,
                                   self._password,
                                   self._timeout)
            self.strPorterrshow = self._SWConn.exctCMD(
                'porterrshow')
            time.sleep(0.25)
            self.strSwitchshow = self._SWConn.exctCMD(
                'switchshow')
            return True
        except Exception as E:
            s.ShowErr(self.__class__.__name__,
                      sys._getframe().f_code.co_name,
                      'Get PortErrorInfo for "{}" Fail with Error:'.format(
                          self._host),
                      '"%s"' % E)

    @s.deco_Exception
    def print_porterrshow(self):
        if self.strPorterrshow:
            print('Porterrshow for SAN Switch "{}":\n'.format(self._host))
            print(self.strPorterrshow)

    @s.deco_Exception
    def print_switchshow(self):
        if self.strSwitchshow:
            print('Switchshow for SAN Switch "{}":\n'.format(self._host))
            print(self.strSwitchshow)

    @s.deco_Exception
    def clear_all_port(self):
        try:
            print('\nStart Clear ALL Error Count For SAN Switch "{}"...'.format(
                self._host))
            self._SWConn.exctCMD('statsclear')
            time.sleep(0.5)
            print('Clear Error Count for SW "{}" Completely...'.format(
                self._host))
        except:
            print('Clear Error Count for SW "{}" Failed!!!'.format(self._host))


    @s.deco_Exception
    def clear_one_port(self, intSWPort):
        try:
            print('Start Clear Port {} For SAN Switch "{}"...'.format(
                str(intSWPort), self._host))
            self._SWConn.exctCMD(
                'portstatsclear {}'.format(str(intSWPort)))
            print('Clear Error Count of Port {} for SW "{}" Completely...\
                '.format(str(intSWPort), self._host))
            return True
        except Exception as E:
            print('Clear Error Count Failed!!!')

    def periodic_check(self, lstCommand, strResultFolder, strResultFile):
        s.GotoFolder(strResultFolder)
        if self._SWConn:
            if self._SWConn.exctCMD('\n'):
                with open(strResultFile, 'w') as f:
                    for strCMD in lstCommand:
                        time.sleep(0.2)
                        strResult = self._SWConn.exctCMD(strCMD)
                        if strResult:
                            print(strResult)
                            f.write(strResult)
                        else:
                            strErr = '\n*** Execute Command "{}" Failed\n'.format(
                                strCMD)
                            print(strErr)
                            f.write(strErr)

class Status(Action):

    def __init__(self, strIP, intPort, strUserName, strPasswd,
                 lstSWPort, intTimeout=2):
        Action.__init__(self, strIP, intPort, strUserName, strPasswd,
                       lstSWPort, intTimeout)
        self._dicPartPortError = None
        self._PutErrorToDict()
        self.strIP=strIP

    '''
    @author: Paul
    @function:  
    get_int输出一种Int值错误数
    get_switch_status 输出一种类型错误在所有端口上的错误总数
    get_switch_total  所有错误总数
    get_switch_original 输入端口报错原始值 输出Int值
    ·_switch_original 输入端口报错原始值 输出int 值
    '''

    @s.deco_Exception
    def _PutErrorToDict(self):

        def _portInLine(intSWPort, strLine):
            lstLine = strLine.split()
            if (str(intSWPort) + ':') in lstLine:
                return True

        def _getErrorAsList(intPortNum, lstPortErrLines):
            for portErrLine in lstPortErrLines:
                if _portInLine(intPortNum, portErrLine):
                    reDataAndErr = re.compile(
                        r'(.*:)((\s+\S+){2})((\s+\S+){6})((\s+\S+){5})(.*)')
                    resultDataAndErr = reDataAndErr.match(portErrLine)
                    return(resultDataAndErr.group(2).split() +
                           resultDataAndErr.group(6).split())

        def _putToDict():
            oddPortError = odd()
            lstPortErrLines = self.strPorterrshow.split('\n')
            for intPortNum in self._allSWPort:
                lstErrInfo = _getErrorAsList(intPortNum, lstPortErrLines)
                oddPortError[intPortNum] = lstErrInfo
            self._dicPartPortError = oddPortError

        if self.strPorterrshow:
            _putToDict()

    def err_num_int(self, strNum):
        if strNum[-1] == 'g':
            return int(float(strNum[:-1]) * 1000000000)
        elif strNum[-1] == 'm':
            return int(float(strNum[:-1]) * 1000000)
        elif strNum[-1] == 'k':
            return int(float(strNum[:-1]) * 1000)
        else:
            return int(strNum)

    def list_string_to_int(self, lstString):
        if lstString:
            return [self.err_num_int(i) for i in lstString]

    def _dict_string_to_int(self, dicPE):
        dicIntPE = odd()
        if dicPE:
            for i in range(len(dicPE.values())):
                port = dicPE.keys()[i]
                lstPortError = dicPE.values()[i]
                dicIntPE[port] = self.list_string_to_int(lstPortError)
            return dicIntPE

    def sum_and_total(self):
        dicIntPE = self._dict_string_to_int(self._dicPartPortError)
        lstSum = []
        total = 0
        for type in range(6):
            sum = 0
            for lstPort in dicIntPE.values():
                sum += lstPort[type]
            lstSum.append(sum)
        for sum in lstSum:
            total += sum
        return lstSum, total

    def sum_total_and_warning(self):
        lstSumTotal = list(self.sum_and_total())
        #return lstSumTotal.append(s.is_Warning(lstSumTotal[1], tuplThresholdTotal))
        intTotal = lstSumTotal[1]
        intWarningLevel = s.is_Warning(intTotal, tuplThresholdTotal)
        lstSumTotalWarning = lstSumTotal.append(intWarningLevel)
        return lstSumTotalWarning
        # 代码还是要给人看的，不光给机器看。。。

    def print_porterror_formated(self):
        tuplDesc = ('Port', 'RX', 'RT', 'EncOut', 'DiscC3', 'LinkFail', 'LossSigle', 'LossSync')
        tuplWidth = (5, 8, 8, 8, 8, 9, 10, 9)

        def _print_description():
            for i in range(len(tuplDesc)):
                print(tuplDesc[i].ljust(tuplWidth[i]), end='')
            print()

        def _print_status_in_line(dicPE):
            if dicPE:
                for port in range(len(dicPE)):
                    print(str(dicPE.keys()[port]).ljust(tuplWidth[0]), end='')
                    for i in range(len(dicPE.values()[port])):
                        print(dicPE.values()[port][i].ljust(tuplWidth[i+1]), end='')
                    print()

        print('\nPort Error Show for SAN Switch "%s":\n' % self._host)
        _print_description()
        _print_status_in_line(self._dicPartPortError)
    
    def switch_status(self):
        dicIntPE_key = self.sum_and_total()[2].keys()
        dicIntPE_values = self.sum_and_total()[2].values()
        dicIntPE  = dict(zip(dicIntPE_key,dicIntPE_values))
        switch_status_key = ['IP',"port"]
        switch_status_values = [host,dicIntPE]
        switch_status = dict(zip(switch_status_key,switch_status_values))
        return switch_status

    @s.deco_Exception
    def get_linkfail_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][4]
            else:
                return 'Please Correct the Port Number...'

    @s.deco_Exception
    def get_encout_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][2]
            else:
                print('Please Correct the Port Number...')


    @s.deco_Exception
    def get_discC3_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][3]
            else:
                print('Please Correct the Port Number...')


def get_Portershow(sw_status):
    DicPE = {}
    sw_PE = sw_status._dicPartPortError
    for port in sw_PE:
        DicPE[port] = sw_PE[port]
    return DicPE


def get_sw_origin(sw_status,sw_ID):
    return {sw_ID: {'IP': sw_status._host,
                    'strSwitchshow': sw_status.strPorterrshow,
                    'porterrshow': sw_status.strSwitchshow}}


def get_sw_summary(sw_status,sw_ID):
    sum_and_total = sw_status.sum_and_total()
    return {sw_ID: {'IP': sw_status._host,
                    'PE_Sum': sum_and_total[0],
                    'PE_Total': sum_and_total[1]}}


def get_sw_status(sw_status,sw_ID):
    return{sw_ID: {'IP': sw_status._host,
                   'PE': get_Portershow(sw_status)}}



def get_dic_all_sw():
    all_sw_origin = {}
    all_sw_summary = {}
    all_sw_status = {}
    for i in range(len(list_sw_IP)):
        sw_status = Status(list_sw_IP[i],ssh_port,user,passwd,list_sw_ports[0])
        all_sw_origin.update(get_sw_origin(sw_status, sw_ID[i]))
        all_sw_summary.update(get_sw_summary(sw_status, sw_ID[i]))
        all_sw_status.update(get_sw_status(sw_status, sw_ID[i]))
    return [all_sw_origin,all_sw_summary,all_sw_status]




if __name__ == '__main__':

    swcfg = gc.SwitchConfig()
    list_sw_IP = swcfg.list_switch_IP()
    list_sw_alias = swcfg.list_switch_alias()
    ssh_port = swcfg.SSH_port()
    user = swcfg.username()
    passwd = swcfg.password()
    list_sw_ports = swcfg.list_switch_ports()


    print(get_dic_all_sw())

    #dic = Status(list_sw_IP[0], ssh_port, user, passwd, list_sw_ports[0])
    #print(get_Portershow(dic))


    #ben
    #print(Status(list_sw_IP[0], ssh_port, user, passwd, list_sw_ports[0]).print_porterror_formated)


