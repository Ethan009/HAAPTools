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


SWITCH_Config = gc.SwitchConfig()
print('telnet_port is %s' % SWITCH_Config.telnet_port())
print('telnet_port is %s' % SWITCH_Config.sw_username())
print('telnet_port is %s' % SWITCH_Config.sw_password())
print('telnet_port is %s' % SWITCH_Config.list_switch_Ports())

# print('telnet_port is %s' % SWITCH_Config.SWTotal_level1())
# print('telnet_port is %s' % SWITCH_Config.SWTotal_level2())
# print('telnet_port is %s' % SWITCH_Config.SWTotal_level3())

# Email_Config = gc.EmailConfig()
# print('EmailConfig is %s' % Email_Config.email_host())
# print('EmailConfig is %s' % Email_Config.email_sender())
# print('EmailConfig is %s' % Email_Config.email_password())
# print('EmailConfig is %s' % Email_Config.email_receiver())
# print('EmailConfig is %s' % Email_Config.email_host())

Setting = gc.Setting()
# print('monitor_web_refresh is %s' % Setting.monitor_web_refresh())
# print('status_upadate is %s' % Setting.status_upadate())
# print('warning_check is %s' % Setting.warning_check())
# print('folder_collection is %s' % Setting.folder_collection())
# print('folder_swporterr is %s' % Setting.folder_swporterr())
# print('folder_trace is %s' % Setting.folder_trace())
# print('folder_traceanalyse is %s' % Setting.folder_traceanalyse())
# print('folder_cfgbackup is %s' % Setting.folder_cfgbackup())
# print('folder_PeriodicCheck is %s' % Setting.folder_PeriodicCheck())
#print('folder_PeriodicCheck is %s' % Setting.PCEngineCommand())
#print('folder_PeriodicCheck is %s' % Setting.PCSANSwitchCommand())

print('folder_PeriodicCheck is %s' % Setting.list_trace_left())
print('folder_PeriodicCheck is %s' % Setting.list_trace_right())

