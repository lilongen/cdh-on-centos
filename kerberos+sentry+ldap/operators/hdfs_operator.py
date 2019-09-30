# coding: utf-8

import subprocess
from .base_operator import BaseOperator
from globals import gv


class HdfsOperator(BaseOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @BaseOperator.cancel_on_error
    def execute(self):
        gv.logger.info('HdfsOperator ...')
        gv.logger.info('set gorup/user directory hdfs permission ...')
        self.set_role_hdfs_home()

    def set_role_hdfs_home(self):
        cmds = []
        credential = gv.conf['hdfs']['credential']
        kinit_hdfs_cmd = 'kinit -k -t {keytab} {principle}'.format(principle=credential['super'], keytab=credential['keytab'])
        cmds.append(kinit_hdfs_cmd)
        for group_mode in gv.conf['group']:
            for g_name, g in gv.conf['group'][group_mode].items():
                if g.get('hdfs_home') is None:
                    continue
                cmds.append('hdfs dfs -mkdir -p {home}'.format(home=g['hdfs_home']))
                cmds.append('hdfs dfs -chgrp -R {group} {home}'.format(group=g_name, home=g['hdfs_home']))
                cmds.append('hdfs dfs -chmod -R g-w {home}'.format(home=g['hdfs_home']))

                if group_mode != 'primary_mode':
                    continue
                for user in g['member']:
                    user_dirs = ['{home}/{user}'.format(home=g['hdfs_home'], user=user), '/user/{user}'.format(user=user)]
                    for dir in user_dirs:
                        cmds.append('hdfs dfs -mkdir -p {user_home}'.format(user_home=dir))
                        cmds.append('hdfs dfs -chown {user} {user_home}'.format(user=user, user_home=dir))
                        cmds.append('hdfs dfs -chgrp -R {group} {user_home}'.format(group=g_name, user_home=dir))

        gv.util.mkdir_p(gv.conf['hdfs']['todo'])
        sh = gv.conf['hdfs']['todo']
        with open(sh, 'w') as f:
            f.write('\n'.join(cmds) + '\n')
        if gv.dryrun:
            return
        subprocess.call('bash %s' % sh, shell=True)