# test.py
import re

str = '''
Product Type : FCE8400G
               Loxoll

Firmware V15.9.7.9      HA-AP Evaluation Build # 001
Revision Data : Horatio Lo(HORATIO-WINX), Aug 15 2018 17:57:13
(C) 1995-2015 Loxoll, Inc. All Rights Reserved.
Redboot(tm) version: 0.2.0.6

Unique ID          : 00000060-22AD0AB2
Unit Serial Number : 11340466
PCB Number         : 11340466
MAC address        : 0.60.22.AD.A.B2
IP addresses       : 172.16.254.72/20.20.20.3

Alert: 913 - Unknown Error
Friday, 4/12/2019, 16:37:57

Port  Node Name           Port Name
A1    2000-006022-ad0ab2  2100-006022-ad0ab2
A2    2000-006022-ad0ab2  2200-006022-ad0ab2
B1    2000-006022-ad0ab2  2300-006022-ad0ab2
B2    2000-006022-ad0ab2  2400-006022-ad0ab2
'''

reNumOfAH = re.compile(r'Alert:\s*(\d*)')
objReNumOfAH = reNumOfAH.search(str)

print(objReNumOfAH.group(1))