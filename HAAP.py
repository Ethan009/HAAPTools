import ClassConnect
import re
from collections import OrderedDict
import os
import sys
import time
import Source as s

import GetConfig as gc

objHAAPConfig = gc.EngineConfig()


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
            print(func.__name__, E)
    return _deco


class HAAP():
    def __init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, intTimeout=3):
        self._host = strIP
        self._TNport = intTNPort
        self._FTPport = intFTPPort
        self._password = strPassword
        self._timeout = intTimeout
        self._TN_Conn = None
        self._FTP_Conn = None
        self._telnet_connect()
        self.AHStatus = _TN_Conn.is_AH()

    def _telnet_connect(self):
        self._TN_Conn = ClassConnect.HAAPConn(self._host,
                                              self._TNport,
                                              self._password,
                                              self._timeout)

    @deco_Exception
    def _executeCMD(self, cmd):
        return self._TN_Conn.exctCMD(cmd)

    def _FTP_connect(self):
        self._FTP_Conn = ClassConnect.FTPConn(self._host,
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

    @deco_OutFromFolder
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

    @deco_Exception
    def updateFW(self, strFWFile):
        connFTP = self._ftp()
        time.sleep(0.25)
        connFTP.PutFile('/mbflash', './', 'fwimage', strFWFile)
        print('FW Upgrade Done for {}, Waiting for reboot...'.format(
            self._host))

    @deco_Exception
    def execute_multi_command(self, strCMDFile):
        tn = self._TN_Conn
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

    @deco_OutFromFolder
    def get_trace(self, strBaseFolder, intTraceLevel):
        tn = self._TN_Conn
        connFTP = self._ftp()
        def _get_oddCommand(intTraceLevel):
            oddCMD = OrderedDict()
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
                    print('Get Trace "{:<10}" for Engine "{}" Failed...\
                        '.format(strTraceDes, self._host))
                #     s.ShowErr(self.__class__.__name__,
                #               sys._getframe().f_code.co_name,
                #               'Get Trace "{:<10}" for Engine "{}" Failed...\
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
                    # Error:'.format(
                    #               lstDescribe[i], self._host),
                    #           E)
                    break
                time.sleep(0.1)

    @deco_OutFromFolder
    def periodic_check(self, lstCommand, strResultFolder, strResultFile):
        tn = self._TN_Conn
        s.GotoFolder(strResultFolder)
        if tn.exctCMD('\n'):
            with open(strResultFile, 'w') as f:
                for strCMD in lstCommand:
                    time.sleep(0.25)
                    strResult = tn.exctCMD(strCMD)
                    if strResult:
                        print(strResult)
                        f.write(strResult)
                    else:
                        strErr = '\n*** Execute Command "{}" Failed\n'.format(
                            strCMD)
                        # print(strErr)
                        f.write(strErr)

    def infoEngine_lst(self):
        # return: [IP, uptime, AH, FW version, status, master, mirror status]
        strVPD = self.get_vpd()

        ip = self._host

        uptime = self.get_uptime(strVPD_Info=strVPD)
        ah = self.get_engine_AH()
        if ah == 0:
            ah = "None"
        elif ah != 0:
            ah = str(ah)

        version = self.get_version(strVPD_Info=strVPD)
        if version is not None:
            version = version[9:]

        # status = self.get_engine_status()
        status = self.get_engine_health()
        master = self.is_master_engine()
        if master is not None:
            if master:
                master = "M"
            else:
                master = ""

        mr_st = self.get_mirror_status()
        if mr_st == 0:
            mr_st = "All OK"
        elif mr_st == -1:
            mr_st = "No Mirror"
        else:
            if mr_st is not None and mr_st != 'RBL':
                mr_st = "NOT ok"

        abts = str(self.get_abts())
        qf = str(self.get_qf())
        a = [ip, uptime, ah, version, status, master, mr_st, abts, qf]
        b = {'IP': ip, 'Uptime': uptime, 'AH': ah, 'Version': version, 'Status': status,
            'Master': master, 'Mirror': mr_st, 'ABTs': abts, 'Qfull': qf}
        return [a, b]
        # return [ip,uptime,ah,version,status,master,mr_st,abts,qf]
        # return {'IP':ip, 'Uptime':uptime, 'AH':ah, 'Version':version, 'Status':status,'Master': master, 'Mirror':mr_st,'ABTs': abts, 'Qfull':qf}

    def set_time(self):
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
            except Exception as E:
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'rtc Set Faild for Engine "{}" with Error:'.format(
                              self._host),
                          '"{}"'.format(E))

        if self._TN_Conn:
            print('\nSetting Time for Engine %s ...' % self._host)
            _exct_cmd()
        else:
            print('\nSetting Time for Engine %s Failed...' % self._host)

    def show_engine_time(self):
        print('Time of Engine "%s":' % self._host)
        if self._TN_Conn:
            try:
                print(self._TN_Conn.exctCMD('rtc').replace(
                    '\nCLI>', '').replace('rtc\r\n', ''))
            except:
                print('Get Time of Engine "%s" Failed' % self._host)


class HAAP_Status(HAAP):
    def __init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, intTimeout=3):
        HAAP.__init__(self, strIP, intTNPort, strPassword,
                      intFTPPort, intTimeout)
        self.dictInfo = _get_info_to_dict()
        self.AHStatus = 

        # cmd_dict = {'vpd': 'vpd', 'engine': 'engine',
        #             'mirror': 'mirror', 'enter': ''}
        # for i in cmd_dict.keys():
        #     setattr(self, i, self._executeCMD(cmd_dict[i]))
        #     time.sleep(0.1)

    def _get_info_to_dict(self):
        lstCommand = ['vpd', 'engine', 'mirror', 'abts', 'qfull']
        dictInfo = {}
        for command in lstCommand:
            dictInfo[command] = self._executeCMD(command)
            time.sleep(0.2)
        return dictInfo

    def get_engine_AH(self):
        if self._TN_Conn:
            strvpd = self._TN_Conn.exctCMD('vpd')
        else:
            self._telnet_connect()
            strvpd = self._TN_Conn.exctCMD('vpd')
        if strvpd is None:
            print("Get vpd Failed for Engine {}".format(self._host))
        else:

            strvpd = self._TN_Conn.exctCMD('vpd')
            listvpd = strvpd.split('\r')
            # print 'lklkl', listvpd
            for i in listvpd:
                if 'Alert' in i:
                    # print i
                    if i == '\nAlert: None':
                        return 0
                        print 'There has no AH in this engine'
                    else:
                        return i[7:] + 'egAH'
                        print "There has some AH in this engine", i

    @deco_Exception
    def get_vpd(self):
        if self._TN_Conn:
            return self._TN_Conn.exctCMD('vpd')
        else:
            self._telnet_connect()
            if self._TN_Conn:
                return self._TN_Conn.exctCMD('vpd')

    def get_engine_health(self):
        # if self.get_engine_status() == "ONLINE":
        if self._TN_Conn:
            strEnter = self._TN_Conn.exctCMD('')
        else:
            self._telnet_connect()
            strEnter = self._TN_Conn.exctCMD('')
        if strEnter is None:
            print("Get Health Status Failed for Engine {}".format(self._host))
        else:
            reAL = re.compile('AH_CLI')
            if reAL.search(strEnter):
                return 'AH_CLI'  # 1 means engine is not healthy (AH)
            else:
                # return 0  # 0 means engine is healthy
                if self._TN_Conn:
                    strEngine = self._TN_Conn.exctCMD('engine')
                else:
                    self._telnet_connect()
                    strEngine = self._TN_Conn.exctCMD('engine')
                if strEngine is None:
                    print "Get Online Status Failed for Engine {}".format(self._host)
                else:
                    reCLI = re.compile(r'>>\s*\d*\s*(\(M\))*\s*Online')
                    if reCLI.search(strEngine):
                        return "ONLINE"
                    else:
                        return "offline"

    def _uptime_list(self, vpd)
    reUpTime = re.compile(
         r'Uptime\s*:\s*((\d*)d*\s*(\d{2}):(\d{2}):(\d{2}))')
     objReUpTime = reUpTime.search(vpd)
      lsUpTime = []
       # add day to list
       try:
            lsUpTime.append(int(result_reUptTime.group(2)))
        except ValueError:
            lsUpTime.append(0)
        # add hr, min, sec to list
        for i in range(3, 6):
            lsUpTime.append(int(result_reUptTime.group(i)))
        return lsUpTime

    def uptime(self):
        return _uptime_list(self.vpd)

    @deco_Exception
    def _is_master_engine(self, strEngine):
        if re.search(r'>>', strEngine):
            reMaster = re.compile(r'(>>)\s*\d*\s*(\(M\))')
            objReMaster = reMaster.search(strEngine)
            if objReMaster is None:
                return False
            else:
                return True

    def master(self):
        return _is_master_engine(self.dictInfo[engine])

    def is_master_engine(self):
        if self._TN_Conn:
            strEngine_info = self._TN_Conn.exctCMD('engine')
        else:
            self._telnet_connect()
            strEngine_info = self._TN_Conn.exctCMD('engine')

        if strEngine_info is None:
            print("Get Master Info Failed for Engine {}".format(self._host))
        else:
            if re.search(r'>>', strEngine_info) is None:
                print("Get Master Info Failed for Engine {}".format(self._host))
            else:
                # e.g. ">> 1  (M)" means current engine is master
                reMaster = re.compile(r'(>>)\s*\d*\s*(\(M\))')
                result_reMaster = reMaster.search(strEngine_info)
                if result_reMaster is None:
                    return False
                else:
                    return True

    @deco_Exception
    def get_mirror_info(self):
        if self._TN_Conn:
            return self._TN_Conn.exctCMD('mirror')
        else:
            self._telnet_connect()
            return self._TN_Conn.exctCMD('mirror')

    @deco_Exception
    def get_mirror_status(self):
        strMirror = self.get_mirror_info()
        if strMirror is None:
            print("Get Mirror Status Failed for Engine {}".format(self._host))
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
                    return error_line  # means mirror not okay
                else:
                    return 0  # 0 means mirror all okay
            else:
                if reNoMirror.search(strMirror):
                    return -1  # -1 means no mirror defined
                else:
                    print("Get Mirror Status Failed for Engine {}".format(self._host))

    @deco_Exception
    def get_version(self, strVPD_Info=None):
        if strVPD_Info is None:
            strVPD_Info = self.get_vpd()
        if strVPD_Info is None:
            print("Get Firmware Version Failed for Engine {}".format(self._host))

        else:
            reFirmware = re.compile(r'Firmware\sV\d+(.\d+)*')
            resultFW = reFirmware.search(strVPD_Info)
            if resultFW:
                return resultFW.group()
            else:
                print("Get Firmware Version Failed for Engine {}".format(self._host))

    def has_abts_qfull(self, SAN_status, ip):
        strVPD = self.get_vpd()
        ports = ['a1', 'a2', 'b1', 'b2']
        # for ip in ips:
        SAN_status[0].update(
            {ip: {'ABTS': '0', 'Qfull': '0', 'Mirror': '0', 'EgReboot': '0'}})
        # print(SAN_status)
        abts = 0
        qf = 0
        for port in ports:

            # print port
            portcmd = 'aborts_and_q_full '
            portcmd += port
            if self._TN_Conn:
                strabts_qf = self._TN_Conn.exctCMD(portcmd)
            else:
                self._telnet_connect()

                if self._TN_Conn:
                    strabts_qf = self._TN_Conn.exctCMD(portcmd)
                    # print(strabts_qf)
            if strabts_qf:
                listabts_qf = strabts_qf.split('\r')
                # print 'asasasasasasa',listabts_qf[8][13]
                abts += int(listabts_qf[2][7])
                qf += int(listabts_qf[8][13])
            else:
                print('default to get abts and qfull')
        #print( abts, qf)
        uptime = self.get_uptime(strVPD_Info=strVPD)
        if uptime:
            #print(uptime, uptime[0], uptime[-2])
            a = uptime.split(':')
            if a[0] == '00' and int(a[-2]) < 30:
                SAN_status[0][ip]['EgReboot'] = '1'

        # print(SAN_status)

    def get_abts(self):

        ports = ['a1', 'a2', 'b1', 'b2']

        abts = 0
        qf = 0
        for port in ports:

            # print port
            portcmd = 'aborts_and_q_full '
            portcmd += port
            if self._TN_Conn:
                strabts_qf = self._TN_Conn.exctCMD(portcmd)
            else:
                self._telnet_connect()
                if self._TN_Conn:
                    strabts_qf = self._TN_Conn.exctCMD(portcmd)
                    print(strabts_qf)
            if strabts_qf:
                listabts_qf = strabts_qf.split('\r')
                abts += int(listabts_qf[2][7])
            else:
                print('default to get abts ')
        #print( abts, qf)
        return abts

    def get_qf(self):

        ports = ['a1', 'a2', 'b1', 'b2']

        abts = 0
        qf = 0
        for port in ports:

            # print port
            portcmd = 'aborts_and_q_full '
            portcmd += port
            if self._TN_Conn:
                strabts_qf = self._TN_Conn.exctCMD(portcmd)
            else:
                self._telnet_connect()
                if self._TN_Conn:
                    strabts_qf = self._TN_Conn.exctCMD(portcmd)
                    print(strabts_qf)
            if strabts_qf:
                listabts_qf = strabts_qf.split('\r')
                qf += int(listabts_qf[8][13])
            else:
                print('default to get qfull')
        return qf

    def get_egw(self):
        # utlist=[0,0]
        abts = self.get_abts()
        qf = self.get_qf()
        mirror = self.get_mirror_status()
        ut = self.get_uptime()
        '''
        if uta >utb:
            ut = 0
        else:
            ut = 1
        utb = uta
        '''
        if ut:
            # print(uptime,uptime[0],uptime[-2])
            a = ut.split(':')
            if a[0] == '00' and int(a[-2]) < 30:
                ut = 1
            else:
                ut = 0
        return {'ABTs': abts, 'Qfull': qf, 'Mirror':mirror,'Reboot':ut}


if __name__ == '__main__':
    # HAAP('10.203.1.111','23','21','password').has_abts_qfull()
    pass
