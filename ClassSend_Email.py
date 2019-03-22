  #!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

# <<<Read Config File Field>>>
objCFG = cp.ConfigParser(allow_no_value=True)
objCFG.read('Conf.ini')
#signal=1

class SEmail(object):
    @staticmethod
    def send_email():
        # << SMTP server >>
        mail_host = objCFG.get('EmailSetting','host')
        mail_user = objCFG.get('EmailSetting','sender')
        mail_password = objCFG.get('EmailSetting','password')

        sender = mail_user
        receivers = objCFG.get('EmailSetting','receiver')
        receivers = receivers.split(',')    #Converting receivers（str） to list
        print receivers


        message = MIMEText('This is HA Appliance emailing for getting help.' + '\n' + \
                           'status', 'plain', 'utf-8')
        #message['From'] = Header(objCFG.get('General','company'), 'utf-8')
        #message['To'] = Header((','.join(receivers)), 'utf-8')
        print type(receivers)
        message['From'] = objCFG.get('General', 'company')
        #message['To'] = objCFG.get('General', 'company')
        message['To'] = ','.join(receivers)
        print message['To']

        #subject = 'SAN Warning......'
        message['Subject'] = Header('Location: '+ objCFG.get('General','location') + '.' + 'SAN Warning......' + ' ' +  'status =' , 'utf-8')#status 之后从数据库拿

        try:
            smtpObj = smtplib.SMTP()

            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            print '2'
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(mail_user, mail_password)
            print '3'
            print type(receivers)
            smtpObj.sendmail(sender, receivers, message.as_string())
            #smtpObj.sendmail(sender, To, message.as_string())
            print "邮件发送成功"
        except smtplib.SMTPException:
            print "Error: 无法发送邮件"

# t=SEmail
# t.send_email(1)