# coding:utf-8

from ftplib import FTP
import telnetlib
import sys
import paramiko
import re
import Source as s


class FTPConn(object):
    def __init__(self, strIP, intPort, strUser, strPWD, intTO):
        self._host = strIP
        self._port = intPort
        self._username = strUser
        self._password = strPWD
        self._timeout = intTO
        self._connected = None
        self._logined = None
        self._Connection = None
        # self._FTPconnect()

    def _FTPconnect(self):
        ftp = FTP()

        def _conn():
            try:
                ftp.connect(self._host, self._port, self._timeout)
                self._connected = ftp
                return True
            except Exception as E:
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'FTP Connect to "{}" Failed with Error:'.format(
                              self._host),
                          '"{}"'.format(E))

        def _login():
            try:
                ftp.login(self._username, self._password)
                self._logined = ftp
                return True
            except Exception as E:
                # print(E)
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'FTP Login to "{}" Failed with Error:'.format(
                              self._host),
                          '"{}"'.format(E))

        if _conn():
            if _login():
                self._Connection = ftp
                return True

    def GetFile(self, strRemoteFolder, strLocalFolder, strRemoteFileName,
                strLocalFileName, FTPtype='bin', intBufSize=1024):
        def _getfile():
            try:
                ftp = self._Connection
                # print(ftp.getwelcome())
                ftp.cwd(strRemoteFolder)
                objOpenLocalFile = open('{}/{}'.format(
                    strLocalFolder, strLocalFileName), "wb")
                if FTPtype == 'bin':
                    ftp.retrbinary('RETR {}'.format(strRemoteFileName),
                                   objOpenLocalFile.write)
                elif FTPtype == 'asc':
                    ftp.retrlines('RETR {}'.format(strRemoteFileName),
                                  objOpenLocalFile.write)
                objOpenLocalFile.close()
                ftp.cwd('/')
                return True
            except Exception as E:
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'FTP Download "{}" Failed with Error:'.format(
                              self._host),
                          '"{}"'.format(E))

        if self._Connection:
            if _getfile():
                return True
        else:
            if self._FTPconnect():
                if _getfile():
                    return True

    def PutFile(self, strRemoteFolder, strLocalFolder, strRemoteFileName,
                strLocalFileName, FTPtype='bin', intBufSize=1024):
        def _putfile():
            try:
                ftp = self._Connection
                # print(ftp.getwelcome())
                ftp.cwd(strRemoteFolder)
                objOpenLocalFile = open('{}/{}'.format(
                    strLocalFolder, strLocalFileName), 'rb')
                if FTPtype == 'bin':
                    ftp.storbinary('STOR {}'.format(strRemoteFileName),
                                   objOpenLocalFile, intBufSize)
                elif FTPtype == 'asc':
                    ftp.storlines('STOR {}'.format(
                        strRemoteFileName), objOpenLocalFile)
                ftp.set_debuglevel(0)
                objOpenLocalFile.close()
                return True
            except Exception as E:
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'FTP Upload "{}" Failed with Error:'.format(
                              self._host),
                          '"{}"'.format(E))

        if self._Connection:
            if _putfile():
                return True
        else:
            if self._FTPconnect():
                if _putfile():
                    return True

    def close(self):
        if self._Connection:
            self._Connection.quit()
            self._Connection = None


class SSHConn(object):
    def __init__(self, host, port, username, password, timeout):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._username = username
        self._password = password
        self.SSHConnection = None
        self._sftp = None
        self.ssh_connect()

    def _connect(self):
        try:
            objSSHClient = paramiko.SSHClient()
            objSSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            objSSHClient.connect(self._host, port=self._port,
                                 username=self._username,
                                 password=self._password,
                                 timeout=self._timeout)
            self.SSHConnection = objSSHClient
            return True
        except Exception as E:
            s.ShowErr(self.__class__.__name__,
                      sys._getframe().f_code.co_name,
                      'SSH Connect to "{}" Failed with Error:'.format(
                          self._host),
                      '"%s"' % E)

    # def download(self, remotepath, localpath):
    #     def _download():
    #         if self._sftp is None:
    #             self._sftp = self.SSHConnection.open_sftp()
    #         self._sftp.get(remotepath, localpath)
    #     try:
    #         _download()
    #     except AttributeError as E:
    #         print(__name__, E)
    #         print('Download Failed,Not Connect to {}'.format(self._host))
    #         return None
    #     else:
    #         print(__name__, E)
    #         print('Download Failed ...')

    # def upload(self, localpath, remotepath):
    #     def _upload():
    #         if self._sftp is None:
    #             self._sftp = self.SSHConnection.open_sftp()
    #         self._sftp.put(localpath, remotepath)
    #     try:
    #         _upload()
    #     except AttributeError as E:
    #         print(__name__, E)
    #         print('Upload Failed,Not Connect to {}'.format(self._host))
    #         return None
    #     else:
    #         print(__name__, E)
    #         print('Upload Failed ...')

    def _connect_retry(self):
        if self.SSHConnection:
            return True
        else:
            print('Connect Retry for SAN Switch "%s" ...' % self._host)
            self._connect()

    def ssh_connect(self):
        self._connect()
        self._connect_retry()


    def exctCMD(self, command):
        def GetRusult():
            stdin, stdout, stderr = self.SSHConnection.exec_command(command)
            data = stdout.read()
            if len(data) > 0:
                # print(data.strip())
                return data
            err = stderr.read()
            if len(err) > 0:
                print('''Excute Command "{}" Failed on "{}" With Error:
    "{}"'''.format(command, self._host, err.strip()))

        def _return(strResult):
            if strResult:
                return strResult
            # else:
            #     s.ShowErr(self.__class__.__name__,
            #               sys._getframe().f_code.co_name,
            #               'Execute Command "{}" Failed with Error:'.format(
            #                   self._host),
            #               E)

        if self.SSHConnection:
            output = _return(GetRusult())
            if output:
                return output

    def close(self):
        if self.ssh_connect:
            self.ssh_connect.close()


class HAAPConn(object):
    def __init__(self, strIP, intPort, strPWD, intTO):
        self._host = strIP
        self._port = intPort
        self._password = strPWD
        self._timeout = intTO
        self._strLoginPrompt = 'Enter password'
        self._strMainMenuPrompt = 'Coredump Menu'
        self._strCLIPrompt = 'CLI>'
        self._strAHPrompt = 'AH_CLI>'
        self._strCLIConflict = 'Another session owns the CLI'
        self.Connection = None
        self.telnet_connect()

    def _connect(self):
        try:
            objTelnetConnect = telnetlib.Telnet(
                self._host, self._port, self._timeout)
            objTelnetConnect.read_until(
                self._strLoginPrompt.encode(encoding="utf-8"), timeout=1)
            objTelnetConnect.write(self._password.encode(encoding="utf-8"))
            objTelnetConnect.write(b'\r')
            objTelnetConnect.read_until(
                self._strMainMenuPrompt.encode(encoding="utf-8"), timeout=1)
            self.Connection = objTelnetConnect
            return True
        except Exception as E:
            s.ShowErr(self.__class__.__name__,
                      sys._getframe().f_code.co_name,
                      'Telnet Connect to "{}" Failed with Error:'.format(
                          self._host),
                      '"{}"'.format(E))

    def _connect_retry(self):
        if self.Connection:
            return True
        else:
            print('Connect Retry for Engine "%s" ...' % self._host)
            self._connect()

    def telnet_connect(self):
        self._connect()
        self._connect_retry()

    def _get_connection_status(self):
        if self.Connection:
            return True
        else:
            return False

    def is_AH(self):
        strPrompt = self.exctCMD('')
        if strPrompt:
            if self._strAHPrompt in strPrompt:
                strVPD = self.exctCMD('vpd')
                reAHNum = re.compile(r'Alert:\s*(\d*)')
                objReAHNum = reAHNum.search(strVPD)
                return int(objReAHNum.group(1))
            else:
                return 0

    def exctCMD(self, strCommand):
        CLI = self._strCLIPrompt.encode(encoding="utf-8")
        CLI_Conflict = self._strCLIConflict.encode(encoding="utf-8")

        def get_result():
            self.Connection.write(
                strCommand.encode(encoding="utf-8") + b'\r')
            strResult = str(self.Connection.read_until(
                CLI, timeout=2).decode())
            if self._strCLIPrompt in strResult:
                return strResult

        def execute_at_CLI():
            # Confirm is CLI or Not
            if self.Connection:
                self.Connection.write(b'\r')
                strEnterOutput = self.Connection.read_until(CLI, timeout=1)

                if CLI in strEnterOutput:
                    return get_result()
                elif 'HA-AP'.encode(encoding="utf-8") in strEnterOutput:
                    self.Connection.write('7')
                    str7Output = self.Connection.read_until(CLI, timeout=1)
                    if CLI in str7Output:
                        return get_result()
                    elif CLI_Conflict in str7Output:
                        self.Connection.write('y')
                        strConfirmCLI = self.Connection.read_until(CLI, timeout=1)
                        if CLI in strConfirmCLI:
                            return get_result()

        if self.Connection:
            return execute_at_CLI()
        # else:
        #     if self._connect():
        #         return execute_at_CLI()
        #     else:
        #         print('Please Check Telnet Connection to "{}" \n\n'.format(
        #             self._host))

    def Close(self):
        if self.Connection:
            self.Connection.close()

    connection = property(
        _get_connection_status, doc="Get HAAPConn instance's connection")


if __name__ == '__main__':

    pass
