# coding: utf-8

from ruamel.yaml import YAML
from jinja2 import Template
from util.mailer import Mailer
from .base_operator import BaseOperator
from ns import ns


class DistributeKeytabOperator(BaseOperator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @BaseOperator.cancel_if_error
    def execute(self):
        ns.logger.info('DistributeKeytabOperator ...')
        ns.logger.info('distribute priciple keytab ...')
        self.distribute_keytab()
        return 0

    def distribute_keytab(self):
        info = ns.conf['mail']
        mailer = Mailer(server=info['server'],
                        sender=info['sender'],
                        username=info['username'],
                        password=info['password'])
        user_keytab = {}
        for username in ns.conf['group']['primary_mode']['g_dev']['member']:
            user_keytab[username] = '{}/{}.keytab'.format(ns.conf['kerberos']['keytab_output_to'], username)

        with open('{cwd}/conf/mail.keytab.distribute.tpl.yml'.format(**ns.tpl_vars), 'r') as f_tpl:
            tpl = f_tpl.read()
        for username, keytab in user_keytab.items():
            ns.tpl_vars['name'] = username
            ns.tpl_vars['kerberos_realm'] = ns.conf['kerberos']['realm']
            mail = YAML().load(Template(tpl).render(**ns.tpl_vars))
            mail['to'] = '%s@yxt.com' % username
            mail['files'] = [keytab]
            ns.logger.info('mail {}.keytab file to {} ...'.format(username, mail['to']))
            if ns.dryrun:
                continue
            mailer.send([mail['to']], mail)
