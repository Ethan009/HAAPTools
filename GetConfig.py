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
    print("11111111111111111")
    def __init__(self):
        #        super(EngineConfig, self).__init__()
        self.cfg = read_config_file()

    def _odd_engines(self):
        oddEngines = Odd()
        for engine in self.cfg.items('Engines'):
            oddEngines[engine[0]] = engine[1]
            lstEngines_alias = list(oddEngines.keys())
            lstEngines_IP = list(oddEngines.values())
        print("lstEngines_alias, lstEngines_IP:",lstEngines_alias, lstEngines_IP)
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

<<<<<<< HEAD


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


        
=======
    
class SwitchConfig(object):
    """docstring for SwitchConfig"""
    print("1111111")

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
            oddSwitcesPorts[switch[0]] = switch[1]
            lstSwitches_alias = list(oddSwitcesPorts.keys())
            lstSwitches_Ports = list(oddSwitcesPorts.values())

        return lstSwitches_alias, lstSwitches_Ports

    def list_switch_alias(self):
        return self.SwitchIP[0]

    def list_switch_IP(self):
        return self.SwitchIP[1]

    def list_switch_Ports(self):
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
        self.Trace = self._odd_oddHAAPErrorDict()
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
    
    def _odd_oddHAAPErrorDict(self):
        oddHAAPErrorDict = Odd()
        for i in self.cfg.items('TraceRegular'):
            oddHAAPErrorDict[i[0]] = i[1]
            Trace_left = list(oddHAAPErrorDict.keys())
            Trace_right = list(oddHAAPErrorDict.values())
        return Trace_left, Trace_right
    def list_trace_left(self):
        return self.Trace[0]
    
    def list_trace_right(self):
        return self.Trace[1]
>>>>>>> optimise_Paul
