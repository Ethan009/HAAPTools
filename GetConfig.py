# coding:utf-8

from collections import OrderedDict as Odd
try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

name_of_config_file = 'conf2.ini'


def read_config_file():
    objCFG = cp.ConfigParser(allow_no_value=True)
    objCFG.read(name_of_config_file)
    return objCFG


class EngineConfig(object):
    """docstring for EngineConfig"""

    def __init__(self):
        #        super(EngineConfig, self).__init__()
        self.cfg = read_config_file()
        self.oddEngines = self._odd_engines()

    def _odd_engines(self):
        oddEngines = Odd()
        for engine in self.cfg.items('Engines'):
            oddEngines[engine[0]] = engine[1]
        return oddEngines

    def list_engines_alias(self):
        return self.oddEngines.keys()

    def list_engines_IP(self):
        return self.oddEngines.values()

    def telnet_port(self):
        return self.cfg.getint('EngineSetting', 'telnet_port')

    def FTP_port(self):
        return self.cfg.getint('EngineSetting', 'ftp_port')

    def password(self):
        return str(self.cfg.get('EngineSetting', 'password'))

    def trace_level(self):
        return self.cfg.getint('EngineSetting', 'trace_level')


class DBConfig(object):
    """docstring for DBConfig"""

    def __init__(self):
        # super(DBConfig, self).__init__()
        self.cfg = read_config_file()

    def host(self):
        return self.cfg.get('DBSetting', 'host')

    def port(self):
        return self.cfg.getint('DBSetting', 'port')

    def name(self):
        return self.cfg.get('DBSetting', 'name')


class SwitchConfig(object):
    """docstring for SwitchConfig"""

    def __init__(self):
        self.cfg = read_config_file()
        self.oddSWAlias = self._odd_switches_Alias()
        self.oddSWPort = self._odd_switches_Ports()

    def _odd_switches_Alias(self):
        oddSWAlias = Odd()
        for sw in self.cfg.items('SANSwitches'):
            oddSWAlias[sw[0]] = sw[1]
        return oddSWAlias

    def _odd_switches_Ports(self):
        oddSWPort = Odd()
        for sw in self.cfg.items('SANSwitchePorts'):
            oddSWPort[sw[0]] = sw[1]
        return oddSWPort

    def list_switch_alias(self):
        return self.oddSWAlias.keys()

    def list_switch_IP(self):
        return self.oddSWAlias.values()

    def list_switch_ports(self):
        return self.oddSWPort.values()

    def SSH_port(self):
        return self.cfg.getint('SANSwitcheSetting', 'ssh_port')

    def username(self):
        return str(self.cfg.get('SANSwitcheSetting', 'username'))

    def password(self):
        return str(self.cfg.get('SANSwitcheSetting', 'password'))

    def SWTotal_level1(self):
        return self.cfg.getint('Threshold', 'SWTotal_level1')

    def SWTotal_level2(self):
        return self.cfg.getint('Threshold', 'SWTotal_level2')

    def SWTotal_level3(self):
        return self.cfg.getint('Threshold', 'SWTotal_level3')


class EmailConfig(object):
    """docstring for EmailConfig"""

    def __init__(self):
        self.cfg = read_config_file()

    def email_host(self):
        return str(self.cfg.get('EmailSetting', 'host'))

    def email_sender(self):
        return str(self.cfg.get('EmailSetting', 'sender'))

    def email_password(self):
        return str(self.cfg.get('EmailSetting', 'password'))

    def email_receiver(self):
        return str(self.cfg.get('EmailSetting', 'receiver'))

    def email_host(self):
        return self.cfg.getint('EmailSetting', 'host_port')


class Setting(object):
    """docstring for Setting"""

    def __init__(self):
        self.cfg = read_config_file()

    def message_level(self):
        return self.cfg.getint('MessageLogging', 'msglevel')

    def monitor_web_refresh(self):
        return self.cfg.getint('RefreshInterval', 'monitor_web_refresh')

    def status_upadate(self):
        return self.cfg.getint('RefreshInterval', 'Status_upadate')

    def warning_check(self):
        return self.cfg.getint('RefreshInterval', 'warning_check')

    def folder_collection(self):
        return str(self.cfg.get('FolderSetting', 'collection'))

    def folder_swporterr(self):
        return str(self.cfg.get('FolderSetting', 'swporterr'))

    def folder_trace(self):
        return str(self.cfg.get('FolderSetting', 'trace'))

    def folder_traceanalyse(self):
        return str(self.cfg.get('FolderSetting', 'traceanalyse'))

    def folder_cfgbackup(self):
        return str(self.cfg.get('FolderSetting', 'cfgbackup'))

    def folder_PeriodicCheck(self):
        return str(self.cfg.get('FolderSetting', 'PeriodicCheck'))

    def PCEngineCommand(self):
        return self.cfg.options("PCEngineCommand")

    def PCSANSwitchCommand(self):
        return self.cfg.options("PCSANSwitchCommand")

    def oddRegularTrace(self):
        oddRegularTrace = Odd()
        for i in self.cfg.items('TraceRegular'):
            oddRegularTrace[i[0]] = i[1]
        return oddRegularTrace

if __name__ == '__main__':
    ec = EngineConfig()
    print(ec.list_engines_alias())

    sc = SwitchConfig()
    print(sc.list_switch_ports())
    pass
