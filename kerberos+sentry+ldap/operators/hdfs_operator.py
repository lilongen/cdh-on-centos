# coding: utf-8

import subprocess
from .base_operator import BaseOperator


class HdfsOperator(BaseOperator):

    def __init__(self, **kwargs):
        super(HdfsOperator, self).__init__(**kwargs)

    def execute(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        logger.info('HdfsOperator ...')
        logger.info('set gorup/user directory hdfs permission ...')
        self.set_role_hdfs_workspace()

    def set_role_hdfs_workspace(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        cmds = []
        credential = conf['hdfs']['credential']
        kinit_hdfs_cmd = 'kinit -k -t {keytab} {principle}'.format(principle=credential['super'], keytab=credential['keytab'])
        cmds.append(kinit_hdfs_cmd)
        for g_name, g in conf['group'].items():
            cmds.append('hdfs dfs -mkdir -p {}'.format(g['hdfs_workspace']))
            cmds.append('hdfs dfs -chgrp -R {} {}'.format(g_name, g['hdfs_workspace']))
            cmds.append('hdfs dfs -chmod -R g+w {}'.format(g['hdfs_workspace']))

        util.mkdir_p(conf['hdfs']['todo'])
        sh = conf['hdfs']['todo']
        with open(sh, 'w') as f:
            f.write('\n'.join(cmds) + '\n')
        if dryrun:
            return
        subprocess.call('bash %s' % sh, shell=True)