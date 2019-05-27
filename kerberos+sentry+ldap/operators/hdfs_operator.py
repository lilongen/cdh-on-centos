# coding: utf-8

import subprocess
from .base_operator import BaseOperator
from ns import ns


class HdfsOperator(BaseOperator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @BaseOperator.cancel_if_error
    def execute(self):
        ns.logger.info('HdfsOperator ...')
        ns.logger.info('set gorup/user directory hdfs permission ...')
        self.set_role_hdfs_home()

    def set_role_hdfs_home(self):
        cmds = []
        credential = ns.conf['hdfs']['credential']
        kinit_hdfs_cmd = 'kinit -k -t {keytab} {principle}'.format(principle=credential['super'], keytab=credential['keytab'])
        cmds.append(kinit_hdfs_cmd)
        for group_mode in ns.conf['group']:
            for g_name, g in ns.conf['group'][group_mode].items():
                if g.get('hdfs_home') is None:
                    continue
                cmds.append('hdfs dfs -mkdir -p {}'.format(g['hdfs_home']))
                cmds.append('hdfs dfs -chgrp -R {} {}'.format(g_name, g['hdfs_home']))
                cmds.append('hdfs dfs -chmod -R g+w {}'.format(g['hdfs_home']))

        ns.util.mkdir_p(ns.conf['hdfs']['todo'])
        sh = ns.conf['hdfs']['todo']
        with open(sh, 'w') as f:
            f.write('\n'.join(cmds) + '\n')
        if ns.dryrun:
            return
        subprocess.call('bash %s' % sh, shell=True)