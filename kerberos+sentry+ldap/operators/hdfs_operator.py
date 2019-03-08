# coding: utf-8

import subprocess
from .base_operator import BaseOperator


class HdfsOperator(BaseOperator):

    def __init__(self, dryrun, logger, conf, util, tpl_vars):
        self.dryrun = dryrun
        self.logger = logger
        self.conf = conf
        self.util = util
        self.tpl_vars = tpl_vars


    def execute(self):
        self.set_role_hdfs_workspace()


    def set_role_hdfs_workspace(self):
        (dryrun, logger, conf, util, tpl_vars) = (self.dryrun, self.logger, self.conf, self.util, self.tpl_vars)
        cmds = []
        credential = conf['hdfs']['credential']
        kinit_hdfs_cmd = 'kinit -k -t {keytab} {principle}'.format(principle=credential['super'], keytab=credential['keytab'])
        cmds.append(kinit_hdfs_cmd)
        for name, r in conf['role'].items():
            cmds.append('hdfs dfs -mkdir -p {}'.format(r['hdfs_workspace']))
            cmds.append('hdfs dfs -chgrp -R {} {}'.format(name, r['hdfs_workspace']))
            cmds.append('hdfs dfs -chmod -R g+w {}'.format(r['hdfs_workspace']))

        util.mkdir(conf['hdfs']['todo'])
        sh = conf['hdfs']['todo']
        f = open(sh, 'w')
        f.write('\n'.join(cmds) + '\n')
        f.close()
        if dryrun:
            return
        subprocess.call('bash %s' % sh, shell=True)