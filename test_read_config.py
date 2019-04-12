# coding:utf-8

import GetConfig as gc

HAAP_Config = gc.EngineConfig()

# print('FTP Port is %s' % HAAP_Config.FTP_port())
pd = HAAP_Config.password()
print('password is %s' % pd)

# print('type of password is %s' % type(HAAP_Config.password()))

# print('type of FTP Port is %s' % type(HAAP_Config.FTP_port()))


# print('All engines %s' % HAAP_Config.list_engines_alias())

# print('type of all engines is %s' % type(HAAP_Config.list_engines_alias()))

# for engine_ip in HAAP_Config.list_engines_IP():
#     print engine_ip


DBcfg = gc.DBConfig()

print('host is %s' % DBcfg.host())

class eval(pd)():
    print('i')