# test.py
import re

# str = '''
# Alert: 913 - Unknown Error
# '''

# reNumOfAH = re.compile(r'Alert:\s*(\d*)')
# objReNumOfAH = reNumOfAH.search(str)

# print(objReNumOfAH.group(1))


import Source as s

print(s.is_Warning(8, (2, 7, 6)))

# print(isinstance((2,7,9), int))
