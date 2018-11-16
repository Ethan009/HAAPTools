# coding:utf-8

from ftplib import FTP
import paramiko
import telnetlib
import sys
import Source as s


def deco_Exception(func):
    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as E:
            print('''
-------------------------------------------------------------------
|    Class Name:     {38}|
|    Function Name:  {38}|
|    Error Message:  {38}|
-------------------------------------------------------------------\
'''.format(self.__class__.__name__, func.__name__, E))
    return _deco


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
                          'FTP Connect to "{}" Fail with Error:'.format(
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
                          'FTP Login to "{}" Fail with Error:'.format(
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
                          'FTP Download "{}" Fail with Error:'.format(
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
                          'FTP Upload "{}" Fail with Error:'.format(
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
        self._client = None
        self._sftp = None
        # self._connect()

    def _connect(self):
        try:
            objSSHClient = paramiko.SSHClient()
            objSSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            objSSHClient.connect(self._host, port=self._port,
                                 username=self._username,
                                 password=self._password,
                                 timeout=self._timeout)
            self._client = objSSHClient
            return True
        except Exception as E:
            s.ShowErr(self.__class__.__name__,
                      sys._getframe().f_code.co_name,
                      'SSH Connect to "{}" Fail with Error:'.format(
                          self._host),
                      '"%s"' % E)

    # def download(self, remotepath, localpath):
    #     def _download():
    #         if self._sftp is None:
    #             self._sftp = self._client.open_sftp()
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
    #             self._sftp = self._client.open_sftp()
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

    def exctCMD(self, command):
        def GetRusult():
            stdin, stdout, stderr = self._client.exec_command(command)
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
            #               'Execute Command "{}" Fail with Error:'.format(
            #                   self._host),
            #               E)

        if self._connect():
            output = _return(GetRusult())
            if output:
                return output
        else:
            print('Please Check SSH Connection to "{}"'.format(self._host))

    def close(self):
        if self._client:
            self._client.close()


class HAAPConn(object):
    def __init__(self, strIP, intPort, strPWD, intTO):
        self._host = strIP
        self._port = intPort
        self._password = strPWD
        self._timeout = intTO
        self._strLoginPrompt = 'Enter password'
        self._strMainMenuPrompt = 'Coredump Menu'
        self._strCLIPrompt = 'CLI>'
        self._strCLIConflict = 'Another session owns the CLI'
        self._Connection = None
        # self._connect()

    # @deco_Exception
    def _connect(self):
        try:
            objTelnetConnect = telnetlib.Telnet(
                self._host, self._port, self._timeout)

            objTelnetConnect.read_until(
                self._strLoginPrompt.encode(encoding="utf-8"), timeout=2)
            objTelnetConnect.write(self._password.encode(encoding="utf-8"))
            objTelnetConnect.write(b'\r')
            objTelnetConnect.read_until(
                self._strMainMenuPrompt.encode(encoding="utf-8"), timeout=2)

            self._Connection = objTelnetConnect
            return True
        except Exception as E:
            s.ShowErr(self.__class__.__name__,
                      sys._getframe().f_code.co_name,
                      'Telnet Connect to "{}" Fail with Error:'.format(
                          self._host),
                      '"{}"'.format(E))

    def _get_connection(self):
        if self._Connection:
            return True
        else:
            return False

    def exctCMD(self, strCommand):

        CLI = self._strCLIPrompt.encode(encoding="utf-8")
        CLI_Conflict = self._strCLIConflict.encode(encoding="utf-8")

        def get_result():
            self._Connection.write(
                strCommand.encode(encoding="utf-8") + b'\r')
            strResult = str(self._Connection.read_until(
                CLI, timeout=3).decode())
            if self._strCLIPrompt in strResult:
                return strResult

        def execute_at_CLI():
            # Confirm is CLI or Not
            self._Connection.write(b'\r')
            strEnterOutput = self._Connection.read_until(CLI, timeout=1)

            if CLI in strEnterOutput:
                return get_result()
            elif 'HA-AP'.encode(encoding="utf-8") in strEnterOutput:
                self._Connection.write('7')
                str7Output = self._Connection.read_until(CLI, timeout=1)
                if CLI in str7Output:
                    return get_result()
                elif CLI_Conflict in str7Output:
                    self._Connection.write('y')
                    strConfirmCLI = self._Connection.read_until(CLI, timeout=1)
                    if CLI in strConfirmCLI:
                        return get_result()

        if self._Connection:
            return execute_at_CLI()
        else:
            if self._connect():
                return execute_at_CLI()
            else:
                print('Please Check Telnet Connection to "{}"'.format(
                    self._host))

    def Close(self):
        if self._Connection:
            self._Connection.close()

    connection = property(_get_connection, doc="Get HAAPConn instance's connection")

if __name__ == '__main__':
    aa = HAAPConn('172.16.254.71', 23, '.com')
    print(aa._Connection)
    # print(aa.exctCMD('conmgr status'))
    # print(1)
    # time.sleep(3)
    # print(aa.exctCMD('conmgr status'))
    # print(2)
    # time.sleep(3)
    # print(aa.exctCMD('conmgr status'))
    # print(3)
    # time.sleep(3)
    # print(aa.exctCMD('conmgr status'))
    # print(4)

    # lstCommand = ['vpd', 'conmgr status', 'mirror', 'explore b1']

    # for i in range(len(lstCommand)):
    #     result = aa.exctCMD(lstCommand[i])
    #     if result:
    #         print result
    #         i += 1
    #     time.sleep(0.25)

    # bb = SSHConn('172.16.254.75', 22, 'admin', 'passwor', 2)
    # x = bb.exctCMD('switchshow')
    # if x:
    #     print(x)
    # print(bb.exctCMD('pwd'))

    # cc = HAAPConn('127.0.0.7', 22, '.com', 5)
    # cc.exctCMD('abc')

    # dd = FTPConn('127.0.0.7', 10021, 'matthew', '.com', 2)
    # if dd.GetFile('.', '.', 'wp.txt', 'bbb'):
    #     print('download wp.txt complate, store as bbb...')
    pass

