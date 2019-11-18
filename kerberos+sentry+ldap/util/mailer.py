#!/usr/bin/env python
# coding: utf-8
#
# Mailer: mail utility tool
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
        # Unless you wish to use has_extn() before sending mail, it should not be necessary to call this method explicitly. It will be implicitly called by sendmail() when necessary.
        # https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.has_extn
        #
        #smtp_cli.ehlo()
        #smtp_cli.starttls() # does not work in py3.7
        #smtp_cli.ehlo()
        smtp_cli.login(self.username, self.password)
        self.smtp_cli = smtp_cli

    def disconnect(self):
        self.smtp_cli.quit()

    def _append_attach(self, mail, files):
        for file in files:
            f = open(file, 'rb')
            attach = MIMEApplication(f.read())
            f.close()
            attach.add_header('Content-Disposition',
                              'attachment',
                              filename=('utf-8', '', file.split('/')[-1]))
            mail.attach(attach)

    def assemble(self, mail_vars: dict):
        mime = MIMEMultipart()
        mime_text = MIMEText(mail_vars['msg'], 'plain', 'utf-8')
        mime.attach(mime_text)
        mime['Subject'] = Header(mail_vars['subject'], 'utf-8').encode()
        mime['To'] = mail_vars['to']
        mime['From'] = self.sender
        if mail_vars.get('from') is not None:
            mime['From'] = mail_vars['from']

        files = mail_vars.get('files')
        if files is not None:
            self._append_attach(mime, files)
        return mime

    def send(self, tolist: list, mail_vars: dict):
        """
        send mail to recipients
        :param tolist: list of recipients
        :param mail_vars: dictionary that includes mail "subject", "from", "msg"
        :return:
        """
        for to in tolist:
            mail_vars['to'] = to
            self.smtp_cli.sendmail(self.sender, to, self.assemble(mail_vars).as_string())

    def send_tpl(self, tolist, tpl_file, tpl_vars):
        """
        send mail that rendered from (tpl_file, tpl_vars) to recipients list
        :param tolist: list of recipients
        :param tpl_file: jinja2 template file that includes mail "subject", "from", "msg".
        :param tpl_vars: template variables used in above template file - tpl_file
        :return:
        """
        with open(tpl_file, 'r') as f_tpl:
            tpl = f_tpl.read()
        mail_vars = YAML().load(Template(tpl).render(**tpl_vars))
        self.send(tolist, mail_vars)
