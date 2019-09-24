# coding: utf-8

import subprocess
from .base_operator import BaseOperator
from globals import gv


class KerberosOperator(BaseOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @BaseOperator.cancel_on_error
    def execute(self):
        gv.logger.info('KerberosOperator ...')
        gv.logger.info('operate principle and generate keytab ...')
        self.operate_principle()

    def operate_principle(self):
        kadmin_with_credential = 'kadmin -p {admin} -w {admin_pw} '
        addprinc_tpl = kadmin_with_credential + 'addprinc -pw lle {username}'
        ktadd_tpl = kadmin_with_credential + 'ktadd -k {keytab_output_to}/{username}.keytab {username}'
        delprinc_tpl = kadmin_with_credential + 'delprinc -force {username}'
        cmds = ''
        vars = gv.conf['kerberos']
        # delete present principal
        for g_name, g in gv.conf['present_group'].items():
            for u in g['member']:
                vars['username'] = u
                cmds += delprinc_tpl.format(**vars) + '\n'

        # add yaml definition user principal
        for g_name, g in gv.conf['group']['primary_mode'].items():
            for u in g['member']:
                vars['username'] = u
                cmds += addprinc_tpl.format(**vars) + '\n'
                cmds += ktadd_tpl.format(**vars) + '\n'

        gv.util.mkdir_p(gv.conf['kerberos']['todo'])
        sh = gv.conf['kerberos']['todo']
        with open(sh, 'w') as f:
            f.write(cmds)

        if gv.dryrun:
            return

        ret = subprocess.call('bash {}'.format(sh), shell=True)
        gv.logger.info(ret)