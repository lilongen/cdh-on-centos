# coding: utf-8

import subprocess
from .base_operator import BaseOperator


class KerberosOperator(BaseOperator):

    def __init__(self, **kwargs):
        super(KerberosOperator, self).__init__(**kwargs)

    def execute(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        logger.info('KerberosOperator ...')
        logger.info('operate principle and generate keytab ...')
        self.operate_principle()

    def operate_principle(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        kadmin_with_credential = 'kadmin -p {admin} -w {admin_pw} '
        addprinc_tpl = kadmin_with_credential + 'addprinc -pw lle {username}'
        ktadd_tpl = kadmin_with_credential + 'ktadd -k {keytab_output_to}/{username}.keytab {username}'
        delprinc_tpl = kadmin_with_credential + 'delprinc -force {username}'
        cmds = ''
        vars = conf['kerberos']
        for r_name, r in conf['role'].items():
            for u in r['user']:
                vars['username'] = u
                cmds += addprinc_tpl.format(**vars) + '\n'
                cmds += ktadd_tpl.format(**vars) + '\n'
        for r_name, r in conf['diff_del']['user'].items():
            for u in r['user']:
                vars['username'] = u
                cmds += delprinc_tpl.format(**vars) + '\n'

        util.mkdir_p(conf['kerberos']['todo'])
        sh = conf['kerberos']['todo']
        with open(sh, 'w') as f:
            f.write(cmds)

        if dryrun:
            return

        ret = subprocess.call('bash {}'.format(sh), shell=True)
        logger.info(ret)