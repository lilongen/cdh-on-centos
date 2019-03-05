#!/usr/bin/env python
# coding: utf-8
#

import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailer():
    server = 'mail.yxt.com:587'
    sender = 'jenkins@yxt.com'
    username = 'jenkins'
    password = 'pwdasdwx'
    smtp: object


    def __init__(self, server=None, sender=None, username=None, password=None):
        self.server = server or self.server
        self.sender = sender or self.sender
        self.username = username or self.username
        self.password = password or self.password

        self._connect()


    def __exit__(self, exc_type, exc_val, exc_tb):
        self._disconnect()


    def _connect(self):
        smtp = smtplib.SMTP()
        smtp.connect(self.server)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(self.username, self.password)
        self.smtp = smtp


    def _disconnect(self):
        self.smtp.quit()


    def _append_attach(self, msg, files):
        for file in files:
            f = open(file, 'rb')
            attach = MIMEApplication(f.read())
            attach.add_header('Content-Disposition',
                              'attachment',
                              filename=('utf-8', '', file.split('/')[-1]))
            msg.attach(attach)
            f.close()


    def assemble(self, msg: dict):
        mime = MIMEMultipart()  # 中文需参数‘utf-8’，单字节字符不需要
        puretext = MIMEText(msg['msg'], 'plain', 'utf-8')
        mime.attach(puretext)
        mime['Subject'] = Header(msg['subject'], 'utf-8').encode()
        mime['To'] = msg['to']
        mime['From'] = self.sender
        if msg.get('from') != None:
            mime['From'] = msg['from']

        files = msg.get('files')
        if files is not None:
            self._append_attach(mime, files)
        return mime


    def send(self, tolist: list, msg: dict):
        for to in tolist:
            msg['to'] = to
            self.smtp.sendmail(self.sender, to, self.assemble(msg).as_string())
