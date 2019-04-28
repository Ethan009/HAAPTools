# coding: utf-8
from __future__ import print_function
from ClassConnect import *
from collections import OrderedDict 
import re
import Source as s
import os
import time
import GetConfig as gc
import array
from functools import total_ordering
objSwitchConfig = gc.SwitchConfig()


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

# 
# def SW():
#     host = objSwitchConfig.list_switch_IP()[1]
#     telnet_port = objSwitchConfig.telnet_port()
#     username = objSwitchConfig.sw_username()
#     password = objSwitchConfig.sw_password()
#     lstSWPort = objSwitchConfig.list_switch_ports()[1]
#     e1 = host, telnet_port, password, username, password, lstSWPort
#     print("e1:", e1)
#     return e1

def _SW(host, lstSWPort):
    return SANSW(host, telnet_port,
                    username, password, lstSWPort)

  

class SANSW():
    def __init__(self, strIP, intPort, strUserName, strPasswd,
                 lstSWPort, intTimeout=2):
        self._host = strIP
        self._port = intPort
        self._username = strUserName
        self._password = strPasswd
        self._timeout = intTimeout
        self._allSWPort = lstSWPort
        self._strAllPortError = None
        self._dicPartPortError = None
        self._SWConn = None
        self._getporterrshow()
        self._PutErrorToDict()

    @deco_Exception
    def _getporterrshow(self):
        try:
            self._SWConn = SSHConn(self._host,
                                   self._port,
                                   self._username,
                                   self._password,
                                   self._timeout)
            self._strAllPortError = self._SWConn.exctCMD(
                'porterrshow')
            return True
        except Exception as E:
            s.ShowErr(self.__class__.__name__,
                      sys._getframe().f_code.co_name,
                      'Get PortErrorInfo for "{}" Fail with Error:'.format(
                          self._host),
                      '"%s"' % E)

    @deco_Exception
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
            oddPortError = OrderedDict()
            lstPortErrLines = str(self._strAllPortError).split('\n')
            for intPortNum in self._allSWPort:
                lstErrInfo = _getErrorAsList(intPortNum, lstPortErrLines)
                oddPortError[intPortNum] = lstErrInfo
            self._dicPartPortError = oddPortError
            print ('aaaaa', oddPortError)
 
        if self._strAllPortError:
            _putToDict()

    @deco_Exception
    def _porterrshow(self):
        if self._strAllPortError:
            print('Porterrshow for SAN Switch {}:\n'.format(self._host))
            print(self._strAllPortError)

    @deco_Exception
    def _switchshow(self):
        if self._SWConn:
            try:
                print('Switchshow for SAN Switch {}:\n'.format(self._host))
                print(self._SWConn.exctCMD('switchshow'))
            except Exception as E:
                pass

    @deco_Exception
    def get_linkfail_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][4]
            else:
                return 'Please Correct the Port Number...'

    @deco_Exception
    def get_encout_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][2]
            else:
                print('Please Correct the Port Number...')
 
    @deco_Exception
    def get_discC3_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][3]
            else:
                print('Please Correct the Port Number...')
 
    @deco_Exception
    def get_encout_total(self):
 
        def _get_count():
            int_encoutTotal = 0
            for i in self._dicPartPortError:
                if 'k' in self._dicPartPortError[i][2]:
                    return 'Over Thousand Errors of encout detected...'
                elif 'm' in self._dicPartPortError[i][2]:
                    return 'Over Million Errors of encout detected...'
                int_encoutTotal += int(self._dicPartPortError[i][2])
            return int_encoutTotal
 
        if self._dicPartPortError:
            return _get_count()
 
    @deco_Exception
    def get_discC3_total(self):
 
        def _get_count():
            int_encoutTotal = 0
            for i in self._dicPartPortError:
                if 'k' in self._dicPartPortError[i][3]:
                    return 'Over Thousand Errors of encout detected...'
                elif 'm' in self._dicPartPortError[i][3]:
                    return 'Over Million Errors of encout detected...'
                int_encoutTotal += int(self._dicPartPortError[i][3])
            return int_encoutTotal
 
        if self._dicPartPortError:
            return _get_count()

    @deco_Exception
    def clear_porterr_All(self):
        try:
            self._SWConn.exctCMD('statsclear')
            print('Clear Error Count for SW "{}" Completely...'.format(
                self._host))
            return True
        except Exception as E:
            print('Clear Error Count for SW "{}" Failed...'.format(self._host))

    @deco_Exception
    def clear_porterr_by_port(self, intSWPort):
        try:
            self._SWConn.exctCMD(
                'portstatsclear {}'.format(str(intSWPort)))
            print('Clear Error Count of Port {} for SW "{}" Completely...\
                '.format(str(intSWPort), self._host))
            return True
        except Exception as E:
            print('Clear Error Count Failed...')


class Status(SANSW):

    def __init__(self, strIP, intPort, strUserName, strPasswd,
                 lstSWPort, intTimeout=2):
        SANSW.__init__(self, strIP, intPort, strUserName, strPasswd,
                 lstSWPort, intTimeout)
    '''
    @author: Paul
    @function:  
    get_int输出一种Int值错误数
    get_switch_status 输出一种类型错误在所有端口上的错误总数
    get_switch_total  所有错误总数
    get_switch_original 输入端口报错原始值 输出Int值                                                                                 ·_switch_original 输入端口报错原始值 输出int 值
    
    '''

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
        dicIntPE = odd()
        for i in range(len(dicPE.values())):
            port = dicPe.keys()[i]
            lstPortError = dicPE.values()[i]
            dicIntPE[port] = self.list_string_to_int(lstPortError)
        print("dicIntPE:",dicIntPE)
        return dicIntPE

    def sum_and_total(self, dicSANSWPorts):
        dicIntPE = self._dict_string_to_int(dicSANSWPorts)
        lstSum = []
        for type in range(6):
            sum = 0
            for lstPort in dicIntPE.values():
                sum += lstPort[type]
            lstSum.append(sum)
        total = sum(lstSum)
        print("lstSum:",lstSum)
        return lstSum,total
    
    
    
    

    # def total(self):
    #     sum(self.sum_all_type(self._dicPartPortError))

    ### 
    
#     def num(self,lisport):
#         for port in range(len(lisport)):
#             if not lisport[port].isdigit():
#                 a=list(lisport[port])
#                 if a[-1] == 'm':
#                     lisport[port]=str(int(float(lisport[port][:-1])*10000))
#                 elif a[-1] == 'k':
#                     lisport[port]=str(int(float(lisport[port][:-1])*1000))
#         
#     #优化每个端口的错误数
#     def get_switch_int(self):
#         lstSwitchstatus = []
#        # a = {}
#         for h in range(len(self._allSWPort)):
#             b = self._dicPartPortError[lstSWPort[h]]
#             self.num(b)
#             lstSwitchstatus.append(b)
#             #加了port的值
#             #a['port' + str(lstSWPort[h])] = b
#         return lstSwitchstatus
#     
#     #每个Ip所有端口每种错误总值
#     def get_switch_status(self):
#         b = self.get_switch_int()
#         total=[0,0,0,0,0,0,0]
#         for a in range(len(b)):
#             total = [total[i]+int(b[a][i]) for i in range(len(b[a]))]
#         return total
#     
#     #所有端口错误总值
#     def get_switch_total(self):
#         b = self.get_switch_status()
#         b = sum(b)
#         return b 

    
    def get_switch_original(self):
        
        return




if __name__ == '__main__':
    
    
    host = objSwitchConfig.list_switch_IP()[0]
    telnet_port = objSwitchConfig.telnet_port()
    username = objSwitchConfig.sw_username()
    password = objSwitchConfig.sw_password()
    lstSWPort = objSwitchConfig.list_switch_ports()[0]
    
    gcsw = gc.SwitchConfig()
    host = gcsw.list_switch_IP()[0]
    port = gcsw.telnet_port()
    username = gcsw.sw_username()
    password = gcsw.sw_password()
    lstSWPort = gcsw.list_switch_ports()[0]
    
    e = host,telnet_port,username,password,lstSWPort
    print("e:",e)
    #SANSW(host,telnet_port,username,password,lstSWPort)._PutErrorToDict()
    Status = Status(host,telnet_port,username,password,lstSWPort).sum_and_total()
