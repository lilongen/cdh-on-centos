# coding: utf-8

from ruamel.yaml import YAML
from jinja2 import Template
from util.mailer import Mailer
from .base_operator import BaseOperator
from globals import gv


class DistributeKeytabOperator(BaseOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @BaseOperator.cancel_if_error
    def execute(self):
        gv.logger.info('DistributeKeytabOperator ...')
        gv.logger.info('distribute priciple keytab ...')
        self.distribute_keytab()
        return 0

    def distribute_keytab(self):
        info = gv.conf['mail']
        mailer = Mailer(server=info['server'],
                        sender=info['sender'],
                        username=info['username'],
                        password=info['password'])
        user_keytab = {}
        for username in gv.conf['group']['primary_mode']['g_dev']['member']:
            user_keytab[username] = '{}/{}.keytab'.format(gv.conf['kerberos']['keytab_output_to'], username)

        with open('{cwd}/conf/mail.keytab.distribute.tpl.yml'.format(**gv.tpl_vars), 'r') as f_tpl:
            tpl = f_tpl.read()
        for username, keytab in user_keytab.items():
            gv.tpl_vars['name'] = username
            gv.tpl_vars['kerberos_realm'] = gv.conf['kerberos']['realm']
            mail = YAML().load(Template(tpl).render(**gv.tpl_vars))
            mail['to'] = '%s@yxt.com' % username
            mail['files'] = [keytab]
            gv.logger.info('mail {}.keytab file to {} ...'.format(username, mail['to']))
            if gv.dryrun:
                continue
            mailer.send([mail['to']], mail)
