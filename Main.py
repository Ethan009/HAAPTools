# coding:utf-8

from __future__ import print_function
import sys
import SANSW as sw
import HAAP as haap
import Source as s
import Monitor as m

try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

import GetConfig as gc

# <<<Get Config Field>>>
setting = gc.Setting()
strCFGFolder = setting.folder_cfgbackup()
strTraceFolder = setting.folder_trace()


# <<<Get Config Field>>>


# <<<Help String Feild>>>
strHelp = '''
        Command   Description

        ptes    : Port Error Show for SAN Switch(s)('porterrshow')
        ptcl    : Clear Port Error Counter('statsclear' or '')
        sws     : Print SAN Switch Info('switchshow')

        gt      : Get Trace of HA-AP Engine(s)
        at      : Analyse Trace of HA-AP Engine(s)
        bc      : Backup Config for HA-AP Engine(s)
        ec      : Execute Commands
        fw      : Change Firmware for HA-AP Engine
        sts     : Show Overall Status for HA-AP Engine(s)
        st      : Sync Time with Local System
        stm     : Show Time Now for HA-AP Engine(s)

        pc      : Periodically Check
        mnt     : Monitor and Show Status throgh Web Server
        '''


strPTESHelp = '''
    Show port error of defined pors as table formatted
    ptes <SW_IP> | all   
        SW_IP  - for defined SAN Switch
        all    - for All SAN Switchs defined in Conf.ini
'''

strPTCLHelp = '''
    Clear Port Error Counter('statsclear' or 'portstatsclear')
    ptcl <SW_IP Port> | all
        SW_IP Port  - for defined Port of defined SAN Switch
        all         - for All SAN Switchs defined in Conf.ini
'''

strSWSHelp = '''
    Print SAN Switch Connect Info('switchshow')
    sws <SW_IP> | all
        SW_IP  - for defined SAN Switch
        all    - for All SAN Switchs defined in Conf.ini
'''

strFWHelp = '''
    Change Firmware for Given Engine Using <FW_File>
    fw <HAAP_IP> <FW_File>
'''

strBCHelp = '''
    Backup Config for HA-AP Engine(s), Save in "{}" Folder
    bc <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''.format(strCFGFolder)


strGTHelp = '''
    Get Trace of HA-AP Engine(s), Save in "{}" Folder
    gt <HAAP_IP> [Trace_Level] | all [Trace_Level]
        HAAP_IP        - for defined HA-AP Engine
        all            - for All HA-AP Engines Defined in Conf.ini
            [Trace_Level]  - Option, Given or Defined
'''.format(strTraceFolder)

# strATHelp = '''
#     Analyse Trace of HA-AP Engine(s), Save in "{}" Folder
#     at <HAAP_IP> [Trace_Level] | all [Trace_Level]
#         HAAP_IP        - for defined HA-AP Engine
#         all            - for All HA-AP Engines Defined in Conf.ini
#             [Trace_Level]  - Option, Given or Defined        
# '''.format(strTraceFolder)

strATHelp = '''
    Analyse Given Trace of HA-AP Engine(s) in Folder <Trace_Folder>
    at <Trace_Folder>
'''

strECHelp = '''
    Execute Commands listed in <Command_File> on Given Engine
    ec <HAAP_IP> <Command_File>
'''

strSTSHelp = '''
    sts <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''

strSTHelp = '''
    st <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini        
'''

strSTMHelp = '''
    stm <HAAP_IP> | all
        HAAP_IP  - for Given HA-AP Engine
        all      - for All HA-AP Engines defined in Conf.ini
'''

strPCHelp = '''
    Periodically Check for HA-AP Engine(s) or SAN Switch(s)
    pc <sw [SW_IP]|haap [HAAP_IP]> | all
        sw SW_IP      - for Given HA-AP Engine
        haap HAAP_IP  - for Given HA-AP Engine
        all           - for All HA-AP Engines and SAN Switches
'''

strMNTHelp = '''
    Show Status Through Web Page
    mnt rt | db
        rt  - Get Status Real Time
        db  - Get Status from DB(Need MongoDB)
'''

# <<<Help String Field>>>


def main():
    if len(sys.argv) == 1:#用户输入参数是否是本身，如果是
        print(strHelp)#打印帮助
    #OK
    elif sys.argv[1] == 'ptes':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strPTESHelp)
        elif sys.argv[2] == 'all':
            sw.print_porterror_all_formated()
        else:
            if s.is_IP(sys.argv[2]):
                sw.print_porterror_formated(sys.argv[2])
            else:
                print('Please Provide Correct Switch IP...')
    #OK
    elif sys.argv[1] == 'ptcl':#判断执行参数是否为ptcl
        num_argv = len(sys.argv)  #获取参数的个数
        if num_argv == 2 or num_argv > 4:#如果是2个或者大于4个
            print(strPTCLHelp) #打印提示信息
        elif sys.argv[2] == 'all': #如果是3个参数是 all
            sw.clear_all() #调用清除所有交换机端口错误函数
        elif s.is_IP(sys.argv[2]):#如果第3个参数是ip的话,判断是不是ip
            if num_argv == 4:   #判断是否有第4个参数，如果有
                #if _isPort(sys.argv[3]):   错误
                if s.is_port(sys.argv[3]):   #在判断第4个参数是否是正确的端口      
                    sw.clear_one_port(sys.argv[2], sys.argv[3])#调用清除具体ip，端口错误
                else:
                    print('Please Provide Correct Port Number...') #请提供正确端口号
            else:
                print(strPTCLHelp) #打印提示
        else:
            print('Please Provide Correct Switch IP...')#请提供正确的交换机ip
    #OK
    elif sys.argv[1] == 'sws':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSWSHelp)
        elif sys.argv[2] == 'all':
            sw.print_switchshow_all()
        else:
            if s.is_IP(sys.argv[2]):
                sw.print_switchshow(sys.argv[2])
            else:
                print('Please Provide Correct Switch IP...')

    #OK
    elif sys.argv[1] == 'bc':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strBCHelp)
        elif sys.argv[2] == 'all':
            haap.backup_config_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.backup_config(sys.argv[2])
            else:
                print('Please Provide Correct Engine IP...')

    # get engines' trace files under TraceFolder based on Trace levels
    #trace、primary、seaond
    #OK git Trace   NOT have Primary
    elif sys.argv[1] == 'gt':
        num_argv = len(sys.argv)
        if num_argv > 3:
            trace_level = int(sys.argv[3])
        if num_argv == 2 or num_argv > 4:
            print(strGTHelp)
        elif sys.argv[2] == 'all':
            if num_argv > 3:
                if s.is_trace_level(trace_level):
                    haap.get_trace_all(trace_level)
                else:
                    print('Trace Level Must Be "1" or "2" or "3"')
            else:
                haap.get_trace_all(0)
        elif s.is_IP(sys.argv[2]):
            if num_argv > 3:
                if s.is_trace_level(trace_level):
                    haap.get_trace(sys.argv[2], trace_level)
                else:
                    print('Trace Level Must Be "1" or "2" or "3"')
            else:
                haap.get_trace(sys.argv[2], 0)
        else:
            print('Please Provide Correct Engine IP...')

    # elif sys.argv[1] == 'at':
    #     num_argv = len(sys.argv)
    #     if num_argv > 3:
    #         trace_level = sys.argv[3]
    #     if num_argv == 2 or num_argv > 4:
    #         print(strPTCLHelp)
    #     elif sys.argv[2] == 'all':
    #         if num_argv > 3:
    #             if s.is_trace_level(trace_level):
    #                 haap.analyse_trace_all(trace_level)
    #             else:
    #                 print('Trace Level Must Be "1" or "2" or "3"')
    #         else:
    #             haap.analyse_trace_all(0)
    #     elif s.is_IP(sys.argv[2]):
    #         if num_argv > 3:
    #             if s.is_trace_level(trace_level):
    #                 haap.analyse_trace(sys.argv[2], trace_level)
    #             else:
    #                 print('Trace Level Must Be "1" or "2" or "3"')
    #         else:
    #             haap.analyse_trace(sys.argv[2], 0)
    #     else:
    #         print('Please Provide Correct Engine IP...')
    #OK python Main.py at Trace\2019-00-00
    elif sys.argv[1] == 'at':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strATHelp)
        else:
            if s.is_folder(sys.argv[2]):
                s.TraceAnalyse(sys.argv[2])
            else:
                print('Please Provide Correct Trace Folder')
    #OK  python Main.py ec 10.203.1.223 cmd.txt
    elif sys.argv[1] == 'ec':
        if len(sys.argv) != 4:
            print(strECHelp)
        else:
            ip = sys.argv[2]
            command_file = sys.argv[3]
            if not s.is_IP(ip):
                print('Please Provide Correct Engine IP...')
            if not s.is_file(command_file):
                print('File Not Exists. Please Provide Correct File...')
            haap.execute_multi_commands(ip, command_file)
    #OK  python Main.py fw 10.203.1.223 FW15.9.7.7_OR.bin
    elif sys.argv[1] == 'fw':
        if len(sys.argv) != 4:
            print(strFWHelp)
        else:
            ip = sys.argv[2]
            fw_file = sys.argv[3]
            if not s.is_IP(ip):
                print('Please Provide Correct Engine IP...')
            if not s.is_file(fw_file):
                print('File Not Exists. Please Provide Correct File...')
            haap.change_firmware(ip, fw_file)
    #OK-
    elif sys.argv[1] == 'sts':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSTSHelp)
        elif sys.argv[2] == 'all':
            haap.show_stauts_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.show_stauts(sys.argv[2])
            else:
                print('Please Provide Correct Engine IP...')
    #OK
    elif sys.argv[1] == 'st':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSTHelp)
        elif sys.argv[2] == 'all':
            haap.set_time_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.set_time(sys.argv[2])
            else:
                print('Please Provide Correct Engine IP...')
    #OK    
    elif sys.argv[1] == 'stm':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSTMHelp)
        elif sys.argv[2] == 'all':
            haap.show_time_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.show_time(sys.argv[2])
            else:
                print('Please Provide Correct Engine IP...')
    #OK
    elif sys.argv[1] == 'pc':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 4:
            print(strPCHelp)
#             print(strPTCLHelp) 原
        elif num_argv > 2:
            if sys.argv[2] == 'all':
                haap.periodically_check_all()
                sw.periodically_check_all()
            elif sys.argv[2] == 'haap':
                if num_argv == 3:
                    haap.periodically_check_all()
                elif num_argv > 3:
                    if s.is_IP(sys.argv[3]):
                        haap.periodically_check(sys.argv[3])
                    else:
                        print('Please Provide Correct Engine IP...')
            elif sys.argv[2] == 'sw':
                if num_argv == 3:
                    sw.periodically_check_all()
                elif num_argv > 3:
                    if s.is_IP(sys.argv[3]):
                        sw.periodically_check(sys.argv[3])
                    else:
                        print('Please Provide Correct SAN Switch IP...')
            else:
                print(strPCHelp)
    #OK
    elif sys.argv[1] == 'mnt':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 4:
            print(strMNTHelp)
        elif sys.argv[2] == 'rt':
            m.monitor_rt_1_thread()
        elif sys.argv[2] == 'db':
            m.monitor_db_4_thread()
        else:
            print('RealTime(rt) or DataBase(db)')

    else:
        print(strHelp)


if __name__ == '__main__':
    main()
