# coding:utf-8

from collections import OrderedDict as Odd
try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

name_of_config_file = 'Config.ini'


def read_config_file():
    objCFG = cp.ConfigParser(allow_no_value=True)
    objCFG.read(name_of_config_file)
    return objCFG


# FolderSetting
collection = 'collections'
swporterr = 'SWPorterr'
trace = 'Trace'
traceanalyse = 'TraceAnalyse'
cfgbackup = 'CFGBackup'
PeriodicCheck = 'PeriodicCheck'

# MessageLogging
msglevel = '1'

# PCEngineCommand
PCEngineCommand_list = ['vpd',
                        'conmgr status',
                        'mirror',
                        'group',
                        'map',
                        'drvstate',
                        'history',
                        'sfp all']

# PCSANSwitchCommand
PCSANSwitchCommand_list = ['ipaddrshow',
                           'switchstatusshow',
                           'switchshow',
                           'porterrshow',
                           'nsshow',
                           'zoneshow',
                           'cfgshow']

# TraceRegular
TraceRegular2 = [['abts_received',
                      "r'(.*)- Port (A1|A2) reports (ABTS received):\s.*(initiator #)(\d+).*(0x.{6})\s?'"],
                 ['abts_frame',
                     "r'(.*)(P0|P1|P2|P3):   (ABTS frame received from port ID )(0x.{6})\s(.*(Initiator number)=(\d+)\s?)?(\s.*)?'"],
                 ['queuefull',
                     "r'(.*)(- Port )(A1|A2)(.*Queue Fulls:\s.*initiator #)(\d+)(.*)(0x.{6})\s?'"],
                 ['linkerror',
                     "r'(.*)(P1|P2|P3|P4): (.*)\((type = )(.*)\)( for our own port)'"],
                 ['driveblocked',
                     "r'(.*) RE: (RE-IOCB) (4504), (address) = (.*),.*\s.*(target_number )(0x.{4}).*.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s.*\s(.*)'"],
                 ['abortcaw',
                     "r'.*(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (.*) - (Aborted Compare and Write command:)\s.*(Drive )(0x.{4}).*(IOCB #)(\d*), (received )(\d*)(.*\s)(.*)'"],
                 ['unwanted_hba',
                     "r'.*(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (.*) - (Port) (A1|A2|B1|B2) (reports initiator arrived:)\s.*(Unwanted initiator at Port ID) (0x.{6}), (WWPN) = (.{16})'"],
                 ['link_error',
                     "r'(\d{2}:\d{2}\.\d{3}\_\d{3}) (P0|P1|P2|P3): (Link error)(.*)'"],
                 ['from_unwant_hba',
                     "r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (.*), (.*) - (Port) (A1|A2|B1|B2) (reports ABTS received):\s.*(From unwanted initiator at Port ID) (.{8})'"],
                 ['lost_connection',
                     "r'\s*(\w{3,6}day), (\d{1,2}/\d{1,2}/20\d{1,2}), (\d{1,2}:\d{1,2}:\d{1,2}) - (Port) (A1|A2|B1|B2) (\w+) (\d+) (bytes of) (\w+) (data):\s+(From drive connection) (\d+) = (drive) #(\d+) (at Port ID) (0x\d{6})'"]]


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
            oddSWPort[sw[0]] = eval(sw[1])
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

    def threshold_total(self):
        lstThreshold = []
        # level1 = self.cfg.getint('Threshold', 'SWTotal_increase_Notify')
        level2 = self.cfg.getint('Threshold', 'SWTotal_increase_Warning')
        level3 = self.cfg.getint('Threshold', 'SWTotal_increase_Alarm')
        # lstThreshold.append(level1)
        lstThreshold.append(level2)
        lstThreshold.append(level3)
        return tuple(lstThreshold)


class EmailConfig(object):
    """docstring for EmailConfig"""

    def __init__(self):
        self.cfg = read_config_file()

    def email_host(self):
        return str(self.cfg.get('EmailSetting', 'host'))

    # port of mail server 
    def email_host_port(self):
        return self.cfg.getint('EmailSetting', 'host_port')

    def email_password(self):
        return str(self.cfg.get('EmailSetting', 'password'))

    def email_sender(self):
        return str(self.cfg.get('EmailSetting', 'sender'))

    def email_receiver(self):
        return str(self.cfg.get('EmailSetting', 'receiver'))

    def email_sub(self):
        return str(self.cfg.get('EmailSetting', 'email_sub'))

    # Whether to Turn off Mail Function
    def email_enable(self):
        return self.cfg.get('EmailSetting', 'enable')


class Setting(object):
    """docstring for Setting"""

    def __init__(self):
        self.cfg = read_config_file()

    def message_level(self):
        return msglevel

    def interval_web_refresh(self):
        return self.cfg.getint('Interval', 'web_refresh')

    def interval_haap_update(self):
        return self.cfg.getint('Interval', 'haap_update')

    def interval_sansw_update(self):
        return self.cfg.getint('Interval', 'sansw_update')

    def interval_warning_check(self):
        return self.cfg.getint('Interval', 'warning_check')

    def folder_collection(self):
        return collection

    def folder_swporterr(self):
        return swporterr

    def folder_trace(self):
        return trace

    def folder_traceanalyse(self):
        return traceanalyse

    def folder_cfgbackup(self):
        return cfgbackup

    def folder_PeriodicCheck(self):
        return PeriodicCheck

    def PCEngineCommand(self):
        return PCEngineCommand_list

    def PCSANSwitchCommand(self):
        return PCSANSwitchCommand_list

    def oddRegularTrace(self):
        oddRegularTrace = Odd()
        for i in TraceRegular2:
            oddRegularTrace[i[0]] = i[1]
        return oddRegularTrace


if __name__ == '__main__':
    pass
