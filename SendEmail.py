#!/usr/bin/env python
#coding:utf8
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


emailcfg=gc.EmailConfig()
email_host=emailcfg.email_host()
email_sender=emailcfg.email_sender()
email_password=emailcfg.email_password()
email_receiver=emailcfg.email_receiver()
email_receiver_list=email_receiver.split(',')
email_host_port=emailcfg.email_host_port()

sub= "用户未确认信息"

def send_warnmail(warninfo_email):
    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = email_sender
    msg['To'] = ",".join(email_receiver_list)
    shuju = ""
    for e in warninfo_email:
        lie = """<tr>
                    <td>""" + str(e[0]) + """</td>
                    <td>""" + str(e[1]) + """</td>
                    <td>""" + str(e[2]) + """</td>
                    <td>""" + str(e[3]) + """</td>
                    <td>""" + str(e[4]) + """</td>
                </tr>"""
        shuju = shuju + lie
    html = """\
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>用户未确认预警信息</title>
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
            <th>IP</th>
            <th>Device</th>
            <th>Level</th>
            <th>Message</th>
          </tr>
          """ + shuju + """
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
        send_smtp.connect(email_host)
        send_smtp.login(email_sender, email_password)
        send_smtp.sendmail(email_sender, email_receiver_list, msg.as_string())
        send_smtp.close()
    except  send_smtp.SMTPException:
        print "Send mail failed!"

def Timely_send(time_now,IP,errlevel,error_massage):

    message = MIMEText('This is HA Appliance emailing for getting help.' + '\n' + \
                       'status is : '  + error_massage + '\n' + \
                        'The time the alarm occurred is' + time_now + '\n' + \
                       'IP is ：' + IP + '\n' + \
                        'The alert level is : ' + str(errlevel) + '\n' + \
                       'plain', 'utf-8')
    message['From'] = email_sender
    message['To'] = ','.join(email_receiver_list)
    message['Subject'] = Header('Your local Data Center have '+ error_massage + '.' ,'utf-8')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(email_host)  # 25 为 SMTP 端口号
        smtpObj.ehlo()
        smtpObj.starttls()

        smtpObj.login(email_sender, email_password)

        smtpObj.sendmail(email_sender, email_receiver_list, message.as_string())

    except smtplib.SMTPException:
        print "Error: NOT SEND Email"
# send_warnmail([['time', '1.1.1.1', 'engine1', 'AH'], ['time', '1.1.1.1', 'engine2', 'AH']])
