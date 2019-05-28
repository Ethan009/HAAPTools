#!/usr/bin/env python
# coding:utf8
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email import encoders
import sys
import os
from datetime import *
import GetConfig as gc


try:
    import configparser as cp
except Exception:
    import ConfigParser as cp


emailcfg = gc.EmailConfig()
email_host = emailcfg.email_host()
email_sender = emailcfg.email_sender()
email_password = emailcfg.email_password()
email_receiver = emailcfg.email_receiver()
email_host_port = emailcfg.email_host_port()


'''warninfo_email = [{'confirm_status':'0',
                   'level':'2',
                   'time_of_send_Email':'2019/1/25 15:00:10',
                   'message':'Engine \'192.168.0.7\' Mirrir Degrade'},{'confirm_status':'0',
                   'level':'2',
                   'time_of_send_Email':'2019/1/25 15:00:10',
                   'message':'Engine \'192.168.0.7\' Mirrir Degrade'}]'''


objCFG = cp.ConfigParser(allow_no_value=True)
objCFG.read('Conf2.ini')
mailto_list = objCFG.get('EmailSetting', 'receiver')


def send_warnmail(warninfo_email):
    mail_host = objCFG.get('EmailSetting', 'host')
    mail_user = objCFG.get('EmailSetting', 'sender')
    mail_pass = objCFG.get('EmailSetting', 'password')
    mailto_list = objCFG.get('EmailSetting', 'receiver')
    mailto_list = mailto_list.split(',')

    me = mail_user
    msg = MIMEMultipart()
    msg['Subject'] = '用户未确认信息'
    msg['From'] = me
    msg['To'] = ",".join(mailto_list)
# 创造数据
   # warninfo_email = queren
    a = os.popen("bash /data/sh/md_sla.sh").read().strip('\n').split(',')

    # 构造html
    d = datetime.now()
    dt = d.strftime('%Y-%m-%d %H:%M:%S')
    at = (d - timedelta(1)).strftime('%Y-%m-%d %H:%M:%S')
    timezone = at + ' ~ ' + dt
# 构造html
    shuju = ""
    for e in warninfo_email:
        lie = """<tr>
                            <td>"""+str(e['time'])+"""</td>
                            <td>"""+str(e['level'])+"""</td>
                            <td>"""+str(e['message'])+"""</td>
                        </tr>"""
        shuju = shuju + lie
    html = """\
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>萌店AB环境</title>
<body>
<div id="container">
  <p><strong>用户未确认预警信息</strong></p>
  
  <div id="content">
   <table width="500" border="2" bordercolor="red" cellspacing="2">
   <div class="container">
        <div class="row">
        <div class="container">
          <tr>
            <th>Time</th>
            <th>Level</th>
            <th>Message</th>
          </tr>
          """+shuju+"""
          </div>
        </div>  
        </div>     
    </table>
  </div>
</body>
</html>
                """

    context = MIMEText(html, _subtype='html', _charset='utf-8')  # 解决乱码
    msg.attach(context)
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(mail_host)
        send_smtp.login(mail_user, mail_pass)
        send_smtp.sendmail(me, mailto_list, msg.as_string())
        print "Send mail succed!"
        send_smtp.close()
        return True
    except send_smtp.SMTPException:
        print "Send mail failed!"


# Klay
def Timely_send(warn_message, warn_level):
    objCFG = cp.ConfigParser(allow_no_value=True)
    objCFG.read('Conf.ini')
    # << SMTP server >>
    mail_host = objCFG.get('EmailSetting', 'host')
    mail_user = objCFG.get('EmailSetting', 'sender')
    mail_password = objCFG.get('EmailSetting', 'password')

    sender = mail_user
    receivers = objCFG.get('EmailSetting', 'receiver')
    receivers = receivers.split(',')  # Converting receivers（str） to list
    s = ''
    for i in range(len(warn_message)):
        s += str(warn_message[i]) + '********' + \
            'Warning level is ' + str(warn_level[i]) + '\n'
    # print receivers

    message = MIMEText('This is HA Appliance emailing for getting help.' + '\n' +
                       'status is : ' + '\n' + s, 'plain', 'utf-8')
    # message['From'] = Header(objCFG.get('General','company'), 'utf-8')
    # message['To'] = Header((','.join(receivers)), 'utf-8')
    # print type(receivers)
    message['From'] = objCFG.get('General', 'company')
    # message['To'] = objCFG.get('General', 'company')
    message['To'] = ','.join(receivers)
    # print message['To']

    # subject = 'SAN Warning......'
    message['Subject'] = Header(
        'Location: ' + objCFG.get('General', 'location') + '.' + 'SAN Warning......' + '\n ', 'utf-8')  # status 之后从数据库拿

    try:
        smtpObj = smtplib.SMTP()

        smtpObj.connect(mail_host)  # 25 为 SMTP 端口号
        print '2'
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_password)
        print '3'
        print type(receivers)
        smtpObj.sendmail(sender, receivers, message.as_string())
        #smtpObj.sendmail(sender, To, message.as_string())
        print "Email Send Success"
    except smtplib.SMTPException:
        print "Error: NOT SEND Email"


# if __name__ == '__main__':

  # main()    # 设置服务器名称、用户名、密码以及邮件后缀
    #send_warnmail(mailto_list, sub,warninfo_email)
'''    
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "657097710@qq.com"  # 用户名3
    mail_pass = "yjnlnqzofsepbebf"  # 口令
    #mailto_lists = sys.argv[1]
    #mailto_list = mailto_lists.split(',')   #发送多人
    #sub= sys.argv[2]
    mailto_list = ['821865224@qq.com']

    sub= "状态sla"

    #send_mail(mailto_list, sub)
    if send_warnmail(mailto_list, sub,queren):
            print "Send mail succed!"
    else:
            print "Send mail failed!"
'''
