# coding:utf-8

from __future__ import print_function
import os
import sys
import time
import re
import Conn as conn
import Source as s
import GetConfig as gc
from collections import OrderedDict as odd

# <<<Get Config Field>>>
objHAAPConfig = gc.EngineConfig()
haapcfg = gc.EngineConfig()
list_engines_IP = haapcfg.list_engines_IP()
list_engines_alias = haapcfg.list_engines_alias()
telnet_port = haapcfg.telnet_port()
FTP_port = haapcfg.FTP_port()
passwd = haapcfg.password()
trace_level_cfg = haapcfg.trace_level()

setting = gc.Setting()
strCFGFolder = setting.folder_cfgbackup()
strTraceFolder = setting.folder_trace()
strPCFolder = setting.folder_PeriodicCheck()
oddHAAPErrorDict = setting.oddRegularTrace()
lstPCCommand = setting.PCEngineCommand()
# <<<Get Config Field>>>


def backup_config_all():
    folder = '%s/%s' % (strCFGFolder, s.time_now_folder())
    for ip in list_engines_IP:
        Action(ip, telnet_port, passwd, FTP_port).backup(folder)


def backup_config(ip):
    folder = '%s/%s' % (strCFGFolder, s.time_now_folder())
    Action(ip, telnet_port, passwd, FTP_port).backup(folder)


def change_firmware(ip, fw_file):
    Action(ip, telnet_port, passwd, FTP_port).change_FW(fw_file)


def get_trace_all(trace_level):
    folder = '%s/%s' % (strTraceFolder, s.time_now_folder())
    if trace_level:
        for ip in list_engines_IP:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level)
    else:
        for ip in list_engines_IP:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level_cfg)


def get_trace(ip, trace_level):
    folder = '%s/%s' % (strTraceFolder, s.time_now_folder())
    try:
        if trace_level:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level)
        else:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level_cfg)
    finally:
        return folder


def analyse_trace_all(trace_level):
    s.TraceAnalyse(oddHAAPErrorDict, get_trace_all(trace_level))


def analyse_trace(ip, trace_level):
    s.TraceAnalyse(oddHAAPErrorDict, get_trace(ip, trace_level))


def execute_multi_commands(ip, command_file):
    Action(ip, telnet_port, passwd, FTP_port).auto_commands(command_file)


tupDesc = ('Engine', 'Status', 'Uptime', 'Master', 'Cluster', 'Mirror')
tupWidth = (18, 15, 15, 8, 9, 8)


def _print_description():
    for i in range(len(tupDesc)):
        print(tupDesc[i].ljust(tupWidth[i]), end='')
    print()


def _print_status_in_line(lstStatus):
    if not lstStatus[1]:
        lstStatus[1] = 'OK'
    if not lstStatus[4]:
        lstStatus[4] = 'OK'
    if not lstStatus[5]:
        lstStatus[5] = 'OK'
    for i in range(len(lstStatus)):
        if lstStatus[i]:
            print(lstStatus[i].ljust(tupWidth[i]), end='')
        else:
            print(''.ljust(tupWidth[i]), end='')
    print()


def show_stauts_all():
    _print_description()
    for ip in list_engines_IP:
        lstStatus = Status(ip, telnet_port, passwd, FTP_port).over_all()
        _print_status_in_line(lstStatus)


def show_stauts(ip):
    _print_description()
    lstStatus = Status(ip, telnet_port, passwd, FTP_port).over_all()
    _print_status_in_line(lstStatus)


def set_time_all():
    for ip in list_engines_IP:
        Action(ip, telnet_port, passwd, FTP_port).set_time()


def set_time(ip):
    Action(ip, telnet_port, passwd, FTP_port).set_time()


def show_time_all():
    for ip in list_engines_IP:
        Action(ip, telnet_port, passwd, FTP_port).show_time()


def show_time(ip):
    Action(ip, telnet_port, passwd, FTP_port).show_time()


def periodically_check_all():
    for ip in list_engines_IP:
        PCFile_name = 'PC_%s_Engine_%s.log' % (
            s.time_now_folder(), ip)
        Action(ip, telnet_port, passwd, FTP_port).periodic_check(
            lstPCCommand, strPCFolder,PCFile_name)


def periodically_check(ip):
    PCFile_name = 'PC_%s_Engine_%s.log' % (
        s.time_now_folder(), ip)
    Action(ip, telnet_port, passwd, FTP_port).periodic_check(
        lstPCCommand, strPCFolder,PCFile_name)


def status_for_judging_realtime(ip):
    objEngine = Status(ip, telnet_port, passwd, FTP_port)
    lstStatus = objEngine.over_all_and_warning()
    intUpTimeSec = objEngine.uptime_second()
    return lstStatus, intUpTimeSec


def list_status_for_realtime_show():
    '''
[['1.1.1.1',0,'2d','M',0,0,0],['1.1.1.1',0,'2d','M',0,1,2]]
    '''
    lstStatus = []
    for i in list_engines_alias:
        objEngine = Status(list_engines_IP[i], telnet_port, passwd, FTP_port)
        lstStatusWarning = list(objEngine.over_all_and_warning())
    return lstStatus


def origin(haap_alias, objEngine):
    dicOrigin = {haap_alias: {'ip': objEngine._host}}
    dicOrigin[haap_alias].update(objEngine.dictInfo)
    return dicOrigin


def info(haap_alias, objEngine):
    lstStatus = objEngine.over_all_and_warning()
    intUpTimeSec = objEngine.uptime_second()

    dicInfo = {haap_alias: {'status': lstStatus[:-1],
                            'up_sec': intUpTimeSec,
                            'level': lstStatus[-1]}}
    return dicInfo


def data_for_db():
    dicInfo = {}
    dicOrigin = {}
    for i in range(len(list_engines_alias)):
        objEngine = Status(list_engines_IP[i], telnet_port, passwd, FTP_port)
        dicInfo.update(info(list_engines_alias[i], objEngine))
        dicOrigin.update(origin(list_engines_alias[i], objEngine))
    return dicOrigin, dicInfo


class Action():
    '''
get_trace
pc
backup
change_FW
emc
stt
st
    '''

    def __init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, intTimeout=1.5):
        self._host = strIP
        self._TNport = intTNPort
        self._FTPport = intFTPPort
        self._password = strPassword
        self._timeout = intTimeout
        self._TN_Conn = None
        self._FTP_Conn = None
        self._TN_Connect_Status = None
        self._telnet_connect()
        self.AHStatus = self._TN_Conn.is_AH()

    def _telnet_connect(self):
        self._TN_Conn = conn.HAAPConn(self._host,
                                      self._TNport,
                                      self._password,
                                      self._timeout)
        self._TN_Connect_Status = self._TN_Conn

    @s.deco_Exception
    def _executeCMD(self, cmd):
        if self._TN_Connect_Status:
            return self._TN_Conn.exctCMD(cmd)

    def _FTP_connect(self):
        self._FTP_Conn = conn.FTPConn(self._host,
                                      self._FTPport,
                                      'adminftp',
                                      self._password,
                                      self._timeout)

    def _ftp(self):
        if self._FTP_Conn:
            connFTP = self._FTP_Conn
        else:
            self._FTP_connect()
            connFTP = self._FTP_Conn
        return connFTP

    @s.deco_OutFromFolder
    def backup(self, strBaseFolder):
        connFTP = self._ftp()
        s.GotoFolder(strBaseFolder)
        lstCFGFile = ['automap.cfg', 'cm.cfg', 'san.cfg']
        for strCFGFile in lstCFGFile:
            if connFTP.GetFile('bin_conf', '.', strCFGFile,
                               'backup_{}_{}'.format(self._host, strCFGFile)):
                print('{} Backup Completely for {}'.format(
                    strCFGFile.ljust(12), self._host))
                continue
            else:
                print('{} Backup Failed for {}'.format(
                    strCFGFile.ljust(12), self._host))
                break
            time.sleep(0.25)

    @s.deco_Exception
    def change_FW(self, strFWFile):
        connFTP = self._ftp()
        time.sleep(0.25)
        connFTP.PutFile('/mbflash', './', 'fwimage', strFWFile)
        print('FW Upgrade Done for {}, Waiting for reboot...'.format(
            self._host))

    @s.deco_Exception
    def auto_commands(self, strCMDFile):
        tn = self._TN_Conn
        if self.AHStatus:
            print("Engine '%s' is at AH Status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return
        with open(strCMDFile, 'r') as f:
            lstCMD = f.readlines()
            for strCMD in lstCMD:
                strResult = tn.exctCMD(strCMD)
                if strResult:
                    print(strResult)
                else:
                    print('\rExecute Command "{}" Failed ...'.format(
                        strCMD))
                    break
                time.sleep(0.5)

    @s.deco_OutFromFolder
    def get_trace(self, strBaseFolder, intTraceLevel):
        if self.AHStatus:
            print("Engine '%s' is at AH Status(AH Code %d)"
                  % (self._host, self.AHStatus))
            return
        tn = self._TN_Conn
        connFTP = self._ftp()

        def _get_oddCommand(intTraceLevel):
            oddCMD = odd()
            if intTraceLevel == 1 or intTraceLevel == 2 or intTraceLevel == 3:
                oddCMD['Trace'] = 'ftpprep trace'
                if intTraceLevel == 2 or intTraceLevel == 3:
                    oddCMD['Primary'] = 'ftpprep coredump primary all'
                    if intTraceLevel == 3:
                        oddCMD['Secondary'] = 'ftpprep coredump secondary all'
                return oddCMD
            else:
                print('Trace Level: 1 or 2 or 3')

        def _get_trace_file(command, strTraceDes):

            # TraceDes = Trace Description
            def _get_trace_name():
                result = tn.exctCMD(command)
                reTraceName = re.compile(r'(ftp_data_\d{8}_\d{6}.txt)')
                strTraceName = reTraceName.search(result)
                if strTraceName:
                    return strTraceName.group()
                else:
                    print('Generate Trace "{}" File Failed for "{}"'.format(
                        strTraceDes, self._host))

            trace_name = _get_trace_name()
            if trace_name:
                time.sleep(0.1)
                local_name = 'Trace_{}_{}.log'.format(self._host, strTraceDes)
                if connFTP.GetFile('mbtrace', '.', trace_name, local_name):
                    print('Get Trace "{:<10}" for "{}" Completely ...'.format(
                        strTraceDes, self._host))
                    return True
                else:
                    print('Get Trace "{:<10}" for Engine "{}" Failed!!!\
                        '.format(strTraceDes, self._host))
                #     s.ShowErr(self.__class__.__name__,
                #               sys._getframe().f_code.co_name,
                #               'Get Trace "{:<10}" for Engine "{}" Failed!!!\
                #               '.format(strTraceDes, self._host))

        oddCommand = _get_oddCommand(intTraceLevel)
        lstCommand = list(oddCommand.values())
        lstDescribe = list(oddCommand.keys())

        if s.GotoFolder(strBaseFolder):
            for i in range(len(lstDescribe)):
                try:
                    if _get_trace_file(lstCommand[i], lstDescribe[i]):
                        continue
                    else:
                        break
                except Exception as E:
                    # s.ShowErr(self.__class__.__name__,
                    #           sys._getframe().f_code.co_name,
                    #           'Get Trace "{}" Failed for Engine "{}",\
                    # Error:'.format(lstDescribe[i], self._host),
                    #           E)
                    break
                time.sleep(0.1)

    @s.deco_OutFromFolder
    def periodic_check(self, lstCommand, strResultFolder, strResultFile):
        print(type(lstCommand))
        if self.AHStatus:
            print("Engine '%s' is at AH Status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return
        tn = self._TN_Conn
        s.GotoFolder(strResultFolder)
        if tn.exctCMD('\n'):
            with open(strResultFile, 'w') as f:
                for strCMD in lstCommand:
                    time.sleep(0.1)
                    strResult = tn.exctCMD(strCMD)
                    if strResult:
                        print(strResult)
                        f.write(strResult)
                    else:
                        strErr = '\n*** Execute Command "{}" Failed\n'.format(
                            strCMD)
                        print(strErr)
                        f.write(strErr)

    def set_time(self):
        if self.AHStatus:
            print("Engine '%s' is at AH Status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return

        def _exct_cmd():
            t = s.TimeNow()

            def complete_print(strDesc):
                print('    Set  %-13s for Engine "%s" Completely...\
                        ' % ('"%s"' % strDesc, self._host))
                time.sleep(0.25)

            try:
                # Set Time
                if self._TN_Conn.exctCMD('rtc set time %d %d %d' % (
                        t.h(), t.mi(), t.s())):
                    complete_print('Time')
                    # Set Date
                    if self._TN_Conn.exctCMD('rtc set date %d %d %d' % (
                            t.y() - 2000, t.mo(), t.d())):
                        complete_print('Date')
                        # Set Day of the Week
                        DoW = t.wd() + 2
                        if DoW == 8:
                            DoW - 7
                        if self._TN_Conn.exctCMD('rtc set day %d' % DoW):
                            complete_print('Day_of_Week')
                return True
            except Exception as E:
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'rtc Set Faild for Engine "{}" with Error:'.format(
                              self._host),
                          '"{}"'.format(E))

        if self._TN_Conn:
            if _exct_cmd():
                print(
                    '\nSetting Time for Engine "%s" Completely...' % 
                    self._host)
            else:
                print('\nSetting Time for Engine "%s" Failed!!!' % self._host)
        else:
            print('\nSetting Time for Engine "%s" Failed!!!' % self._host)

    def show_time(self):
        if self.AHStatus:
            print("Engine '%s' is at AH Status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return
        print('Time of Engine "%s":' % self._host)
        if self._TN_Conn:
            try:
                print(self._TN_Conn.exctCMD('rtc').replace(
                    '\nCLI>', '').replace('rtc\r\n', ''))
            except BaseException:
                print('Get Time of Engine "%s" Failed' % self._host)


class Uptime(object):
    """docstring for uptime"""

    def __init__(self, strVPD):
        self.vpd = strVPD
        self.list_uptime = self._uptime_list()

    def _uptime_list(self):
        if self.vpd:
            reUpTime = re.compile(
                r'Uptime\s*:\s*((\d*)d*\s*(\d{2}):(\d{2}):(\d{2}))')
            objReUpTime = reUpTime.search(self.vpd)
            lstUpTime = []
           # add day to list
            try:
                lstUpTime.append(int(objReUpTime.group(2)))
            except ValueError:
                lstUpTime.append(0)
            # add hr, min, sec to list
            for i in range(3, 6):
                lstUpTime.append(int(objReUpTime.group(i)))
            return lstUpTime

    def uptime_list(self):
        if self.vpd:
            return self._uptime_list()

    def uptime_second(self):
        uptime_list = self.uptime_list()
        if uptime_list:
            intSecond = 0
            # d, h, m, s means days hours minutes seconds
            d = uptime_list[0]
            h = uptime_list[1]
            m = uptime_list[2]
            s = uptime_list[3]
            if d:
                intSecond += d * 24 * 3600
            if h:
                intSecond += h * 3600
            if m:
                intSecond += m * 60
            if s:
                intSecond += s
            return intSecond

    def uptime_to_show(self):
        uptime_list = self.uptime_list()
        if uptime_list:
            # d, h, m, s means days hours minutes seconds
            d = uptime_list[0]
            h = uptime_list[1]
            m = uptime_list[2]
            s = uptime_list[3]
            if d:
                return '%dd %dh %dm' % (d, h, m)
            elif h:
                return '%dh %dm %ds' % (h, m, s)
            elif m:
                return '%dm %ds' % (m, s)
            else:
                return '%d Seconds' % s


class Status(Action):

    def __init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, intTimeout=5):
        Action.__init__(self, strIP, intTNPort, strPassword,
                        intFTPPort, intTimeout)
        # self._telnet_connect()
        self.dictInfo = self._get_info_to_dict()
        self.uptime = Uptime(self.dictInfo['vpd'])

    @s.deco_Exception
    def _get_info_to_dict(self):
        if self.AHStatus:
            print("Engine '%s' is at AH Status(AH Code %d)"
                  % (self._host, self.AHStatus))
            return
        lstCommand = ['vpd', 'engine', 'mirror']
        dictInfo = {}
        if self._TN_Connect_Status:
            for command in lstCommand:
                dictInfo[command] = self._executeCMD(command)
                time.sleep(0.2)
            return dictInfo

    def uptime_list(self):
        return self.uptime.uptime_list()

    def uptime_second(self):
        return self.uptime.uptime_second()

    def uptime_to_show(self):
        return self.uptime.uptime_to_show()

    @s.deco_Exception
    def _is_master(self, strEngine):
        if strEngine is None:
            return
        if re.search(r'>>', strEngine):
            reMaster = re.compile(r'(>>)\s*\d*\s*(\(M\))')
            objReMaster = reMaster.search(strEngine)
            if objReMaster:
                return 'M'

    @s.deco_Exception
    def is_master(self):
        if self.dictInfo['engine']:
            return self._is_master(self.dictInfo['engine'])

    def cluster_status(self):
        if self.dictInfo['engine']:
            if 'offline' in self.dictInfo['engine']:
                return True

    def get_version(self):
        if self.dictInfo['vpd'] is None:
            return
        strVPD = self.dictInfo['vpd']
        reFirmWare = re.compile(r'Firmware\sV\d+(.\d+)*')
        resultFW = reFirmWare.search(strVPD)
        if resultFW:
            return resultFW.group().replace('Firmware ', '')
        else:
            print('Get Firmware Version Failed for Engine "%s"' % self._host)

# ## Matt Need to be optimise...
    @s.deco_Exception
    def get_mirror_status(self):
        strMirror = self.dictInfo['mirror']
        if strMirror is None:
            print('Get Mirror Status Failed for Engine "%s"' % self._host)
        else:
            reMirrorID = re.compile(r'\s\d+\(0x\d+\)')  # e.g." 33281(0x8201)"
            reNoMirror = re.compile(r'No mirrors defined')

            if reMirrorID.search(strMirror):
                error_line = ""
                reMirrorStatus = re.compile(r'\d+\s\((\D*)\)')  # e.g."2 (OK )"
                lines = list(filter(None, strMirror.split("\n")))

                for line in lines:
                    if reMirrorID.match(line):
                        mirror_ok = True
                        mem_stat = reMirrorStatus.findall(line)
                        for status in mem_stat:
                            if status.strip() != 'OK':
                                mirror_ok = False
                        if not mirror_ok:
                            error_line += line + "\n"
                if error_line:
                    # print('mirror:',error_line)
                    return 1 # means mirror not okay
                else:
                    return 0  # 0 means mirror all okay
            else:
                if reNoMirror.search(strMirror):
                    return -1  # -1 means no mirror defined
                else:
                    print('Get Mirror Status Failed for Engine "%s"' % 
                          self._host)
    #update lststatus
    def over_all(self):
        '''list of over all'''
        lstOverAll = []
        lstOverAll.append(self._host)
        if self.AHStatus == None:
            lstOverAll.append("AH")
            for i in range(4):
                lstOverAll.append('--')
        else:
            lstOverAll.append("OK")
            lstOverAll.append(self.uptime_to_show())
            lstOverAll.append(self.is_master())
            lstOverAll.append(self.cluster_status())
            if self.get_mirror_status() == 1:
                lstOverAll.append('Not OK')
            else:
                lstOverAll.append(str(self.get_mirror_status()))
        return lstOverAll

    def over_all_and_warning(self):
        lstStatus = self.over_all()
        if any([lstStatus[i] for i in [1, 4, 5]]):
            lstStatus.append(2)
        else:
            lstStatus.append(0)
        return lstStatus


if __name__ == '__main__':
    pass
