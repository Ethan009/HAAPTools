# test.py
import re
import HAAP as h
import GetConfig as gc
hconf = gc.EngineConfig()
from collections import OrderedDict as Odd
import SendEmail as SE
# str = '''
# Alert: 913 - Unknown Error
# '''

# reNumOfAH = re.compile(r'Alert:\s*(\d*)')
# objReNumOfAH = reNumOfAH.search(str)

# print(objReNumOfAH.group(1))


# import Source as s

# print(s.is_Warning(8, (2, 7, 6)))

# # print(isinstance((2,7,9), int))
SE.send_warnmail([{'time':'10.23.445' , 'IP': '12.23.45.2' , 'level' : 34 , 'message' : 'engine reboot'},
                  {'time': '10.23.445', 'IP': '12.23.45.2', 'level': 34, 'message': 'engine reboot'},
                  {'time': '10.23.445', 'IP': '12.23.45.2', 'level': 34, 'message': 'engine reboot'},
                  {'time': '10.23.445', 'IP': '12.23.45.2', 'level': 34, 'message': 'engine reboot'},
                  {'time': '10.23.445', 'IP': '12.23.45.2', 'level': 34, 'message': 'engine reboot'},
                  {'time': '10.23.445', 'IP': '12.23.45.2', 'level': 34, 'message': 'engine reboot'}])
SE.Timely_send('2019/05/23 10:20:30','10.203.1.231',5,'Engine reboot')


# lstEngine = hconf.list_engines_IP()
# intTNPort = hconf.telnet_port()
# intFTPPort = hconf.FTP_port()
# strPassword = hconf.password()
#
#
#
# oddEngineInstance = Odd()
# for engine in lstEngine:
#     oddEngineInstance[engine] = h.Status(engine,
#         intTNPort,
#         strPassword,
#         intFTPPort)
#
#     print oddEngineInstance[engine].dictInfo



# ditEngineStatus = {}
# for engine in lstEngine:
#     ditEngineStatus[engine] = oddEngineInstance[engine]
#
# print ditEngineStatus


#Ethan

