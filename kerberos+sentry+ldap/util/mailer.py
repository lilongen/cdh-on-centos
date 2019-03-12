#!/usr/bin/env python
# coding: utf-8
#
# known issue:
#   cause python3.7 openssl changes, smtp = smtplib.SMTP().starttls() will failed
#   so this mailer does not work at python3.7
#
import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ruamel.yaml import YAML
from jinja2 import Template


class Mailer(object):
    server = 'mail.yxt.com:587'
    sender = 'jenkins@yxt.com'
    username = 'jenkins'
    password = 'pwdasdwx'
    smtp_cli: object

    def __init__(self, server=None, sender=None, username=None, password=None):
        self.server = server or self.server
        self.sender = sender or self.sender
        self.username = username or self.username
        self.password = password or self.password

        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        smtp_cli = smtplib.SMTP()
        smtp_cli.connect(self.server)
        smtp_cli.ehlo()
        smtp_cli.starttls() # does not work in py3.7
        smtp_cli.ehlo()
        smtp_cli.login(self.username, self.password)
        self.smtp_cli = smtp_cli

    def disconnect(self):
        self.smtp_cli.quit()

    def _append_attach(self, mail, files):
        for file in files:
            print(file)
            f = open(file, 'rb')
            attach = MIMEApplication(f.read())
            attach.add_header('Content-Disposition',
                              'attachment',
                              filename=('utf-8', '', file.split('/')[-1]))
            mail.attach(attach)
            f.close()

    def assemble(self, mail: dict):
        mime = MIMEMultipart()  # 中文需参数‘utf-8’，单字节字符不需要
        puretext = MIMEText(mail['msg'], 'plain', 'utf-8')
        mime.attach(puretext)
        mime['Subject'] = Header(mail['subject'], 'utf-8').encode()
        mime['To'] = mail['to']
        mime['From'] = self.sender
        if mail.get('from') is not None:
            mime['From'] = mail['from']

        files = mail.get('files')
        if files is not None:
            self._append_attach(mime, files)
        return mime

    def send(self, tolist: list, mail: dict):
        for to in tolist:
            mail['to'] = to
            self.smtp_cli.sendmail(self.sender, to, self.assemble(mail).as_string())

    def send_tpl(self, tolist, tpl_file, tpl_vars):
        with open(tpl_file, 'r') as f_tpl:
            tpl = f_tpl.read()
        mail = YAML().load(Template(tpl).render(**tpl_vars))
        self.send(tolist, mail)
