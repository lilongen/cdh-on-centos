# coding: utf-8

from ruamel.yaml import YAML
from jinja2 import Template
from util.mailer import Mailer
from .base_operator import BaseOperator


class DistributeKeytabOperator(BaseOperator):

    def __init__(self, **kwargs):
        super(DistributeKeytabOperator, self).__init__(**kwargs)


    def execute(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        logger.info('DistributeKeytabOperator ...')
        logger.info('distribute priciple keytab ...')
        self.distribute_keytab()


    def distribute_keytab(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        info = conf['mail']
        mailer = Mailer(server=info['server'],
                        sender=info['sender'],
                        username=info['username'],
                        password=info['password'])
        user_keytab = {}
        for r_name, r in conf['role'].items():
            for username in r['user']:
                user_keytab[username] = '{}/{}.keytab'.format(conf['kerberos']['keytab_output_to'], username)

        f_tpl = open('{cwd}/conf/mail.keytab.distribute.tpl.yml'.format(**tpl_vars), 'r')
        tpl = f_tpl.read()
        f_tpl.close()
        for username, keytab in user_keytab.items():
            tpl_vars['name'] = username
            tpl_vars['kerberos_realm'] = conf['kerberos']['realm']
            mail = YAML().load(Template(tpl).render(**tpl_vars))
            mail['to'] = '%s@yxt.com' % username
            mail['files'] = [keytab]
            logger.info('mail {}.keytab file to {} ...'.format(username, mail['to']))
            if dryrun:
                continue
            mailer.send([mail['to']], mail)
