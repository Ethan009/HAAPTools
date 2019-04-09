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
