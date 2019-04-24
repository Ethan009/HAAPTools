# test.py
import re
import HAAP as h
import GetConfig as gc
hconf = gc.EngineConfig()
from collections import OrderedDict as Odd
# str = '''
# Alert: 913 - Unknown Error
# '''

# reNumOfAH = re.compile(r'Alert:\s*(\d*)')
# objReNumOfAH = reNumOfAH.search(str)

# print(objReNumOfAH.group(1))


# import Source as s

# print(s.is_Warning(8, (2, 7, 6)))

# # print(isinstance((2,7,9), int))

lstEngine = hconf.list_engines_IP()
intTNPort = hconf.telnet_port()
intFTPPort = hconf.FTP_port()
strPassword = hconf.password()

oddEngineInstance = Odd()
for engine in lstEngine:
    oddEngineInstance[engine] = h.HAAP(engine,
        intTNPort,
        strPassword,
        intFTPPort)

ditEngineStatus = {}
for engine in lstEngine:
     ditEngineStatus[engine] = oddEngineInstance[engine]

print ditEngineStatus