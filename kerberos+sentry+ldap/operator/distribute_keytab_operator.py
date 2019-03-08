# coding: utf-8

from ruamel.yaml import YAML
from .operator import Operator
from ..util.mailer import Mailer


class DistributeKeytabOperator(Operator):

    def __init__(self, dryrun, logger, conf, util, tpl_vars):
        self.dryrun = dryrun
        self.logger = logger
        self.conf = conf
        self.util = conf
        self.tpl_vars = tpl_vars


    def execute(self):
        self.set_role_hdfs_workspace()


    def distribute_keytab(self):
        (dryrun, logger, conf, util, tpl_vars) = (self.dryrun, self.logger, self.conf, self.util, self.tpl_vars)
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
