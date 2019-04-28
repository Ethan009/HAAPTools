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

setting = gc.Setting()
lstPCCommand = setting.PCEngineCommand()
strPCFolder = setting.folder_PeriodicCheck()
# <<<Get Config Field>>>


def deco_OutFromFolder(func):
    strOriFolder = os.getcwd()

    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            # print(func.__name__, E)
            pass
        finally:
            os.chdir(strOriFolder)
    return _deco


def deco_Exception(func):
    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            print(self._host, func.__name__, E)
    return _deco


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
    for ip in list_sw_IP:
        Action(ip, ssh_port, user, passwd, []).print_porterrshow()

def print_porterror_formated(ip):
    Action(ip, ssh_port, user, passwd, []).print_porterrshow()

def print_switchshow_all():
    for ip in list_sw_IP:
        Action(ip, ssh_port, user, passwd, []).print_switchshow()

def print_switchshow(ip):
    Action(ip, ssh_port, user, passwd, []).print_switchshow()


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
            print(self.switchshow)

    @s.deco_Exception
    def clear_all_port(self):
        if self._SWConn.exctCMD('statsclear'):
            print('Clear Error Count for SW "{}" Completely...'.format(
                self._host))
            return True
        else:
            print('Clear Error Count for SW "{}" Failed!!!'.format(self._host))

    @s.deco_Exception
    def clear_one_port(self, intSWPort):
        try:
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
            lstPortErrLines = str(self.strPorterrshow).split('\n')
            for intPortNum in self._allSWPort:
                lstErrInfo = _getErrorAsList(intPortNum, lstPortErrLines)
                oddPortError[intPortNum] = lstErrInfo
            self._dicPartPortError = oddPortError

        if self.strPorterrshow:
            _putToDict()

    def err_num_int(self, strNum):
        if strNum[-1] == 'g':
            return int(float(strNum[:-1])*1000000000)
        elif strNum[-1] == 'm':
            return int(float(strNum[:-1])*1000000)
        elif strNum[-1] == 'k':
            return int(float(strNum[:-1])*1000)
        else:
            return int(strNum)

    def list_string_to_int(self, lstString):
        return [self.err_num_int(i) for i in lstString]

    def _dict_string_to_int(self, dicPE):
        print(dicPE)
        dicIntPE = odd()
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

    def print_porterror_formated():
        tuplDesc = ('Port', 'RX', 'RT' 'EncOut', 'DiscC3', 'LinkFail', 'LossSigle', 'LossSync')
        tuplWidth = (3, 8, 8, 6, 6, 6, 6, 6)

        def _print_description():
            for i in range(len(tupDesc)):
                print(tupDesc[i].center(tupWidth[i]), end='')
            print()

        def _print_status_in_line(dicPE):
            for port in range(len(dicPE)):
                print(dicPE.keys()[port].center(tuplWidth[0]), end='')
                for i in dicPE.values()[port]:
                    print(dicPE.keys()[i].center(tupWidth[i+1]), end='')
                print()

        print('Port Error Show for SAN Switch "%s":\n' % self._host)
        _print_description()
        _print_status_in_line(self._dicPartPortError)


 #      dictEngines = _get_HAAPInstance()
 # 1084      tupDesc = ('Engine', 'AH', 'Uptime', 'FirmWare', 'Master', 'Mirror')
 # 1085:     tupWidth = (18, 16, 20, 13, 9, 12)
 # 1086  
 # 1087      def _print_description():
 # 1088          for i in range(len(tupDesc)):
 # 1089:             print(tupDesc[i].center(tupWidth[i]), end='')
 # 1090          print()
 # 1091           
 # 1092      def _print_status_in_line(lstStatus):
 # 1093          for i in range(len(lstStatus)):
 # 1094:             print(lstStatus[i].center(tupWidth[i]), end='')
 # 1095          print()



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


if __name__ == '__main__':

    gcsw = gc.SwitchConfig()
    host = gcsw.list_switch_IP()[0]
    port = gcsw.ssh_port()
    username = gcsw.sw_username()
    password = gcsw.sw_password()
    lstPort = gcsw.list_switch_ports()[0]

    # SANSW(host,ssh_port,username,password,lstSWPort)._PutErrorToDict()
    s1 = Status(host, port, username, password, lstPort).sum_and_total()
    print(s1)
