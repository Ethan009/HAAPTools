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

    def _odd_engines(self):
        oddEngines = Odd()
        for engine in self.cfg.items('Engines'):
            oddEngines[engine[0]] = engine[1]
            lstEngines_alias = list(oddEngines.keys())
            lstEngines_IP = list(oddEngines.values())
        return lstEngines_alias, lstEngines_IP

    def list_engines_alias(self):
        return self._odd_engines()[0]

    def list_engines_IP(self):
        return self._odd_engines()[1]

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
        self.SwitchIP = self._odd_switches()
        self.SwitchPorts = self._odd_switches_Ports()

    def _odd_switches(self):
        oddSwitces = Odd()
        for switch in self.cfg.items('SANSwitches'):
            oddSwitces[switch[0]] = switch[1]
            lstSwitches_alias = list(oddSwitces.keys())
            lstSwitches_IP = list(oddSwitces.values())
        return oddSwitces, lstSwitches_IP
    
    def _odd_switches_Ports(self):
        oddSwitcesPorts = Odd()
        for switch in self.cfg.items('SANSwitchePorts'):
            oddSwitcesPorts[switch[0]] = eval(switch[1])
            lstSwitches_alias = list(oddSwitcesPorts.keys())
            print("1234:",lstSwitches_alias)
            lstSwitches_Ports = oddSwitcesPorts.values()
            print("wqeqwe:",type(lstSwitches_Ports[0]))
#             lstSwitches_Ports = lstSwitches_Ports.split()
        return lstSwitches_alias, lstSwitches_Ports

    def list_switch_alias(self):
        return self.SwitchIP[0]

    def list_switch_IP(self):
        return self.SwitchIP[1]

    def list_switch_ports(self):
        return self.SwitchPorts[1]

    def telnet_port(self):
        return self.cfg.getint('SANSwitcheSetting', 'port')

    def sw_username(self):
        return str(self.cfg.get('SANSwitcheSetting', 'username'))

    def sw_password(self):
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
        return str(self.cfg.options("PCEngineCommand"))
    
    def PCSANSwitchCommand(self):  
        return str(self.cfg.options("PCSANSwitchCommand"))
    
    def oddRegularTrace(self):
        oddRegularTrace = Odd()
        for i in self.cfg.items('TraceRegular'):
            oddRegularTrace[i[0]] = i[1]
        return oddRegularTrace



