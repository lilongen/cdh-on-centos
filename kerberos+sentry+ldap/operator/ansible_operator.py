# coding: utf-8

from ruamel.yaml import YAML
import subprocess
from .operator import Operator


class AnsibleOperator(Operator):

    def __init__(self, dryrun, logger, conf, util, tpl_vars):
        self.dryrun = dryrun
        self.logger = logger
        self.conf = conf
        self.util = conf
        self.tpl_vars = tpl_vars

    def execute(self):
        self.generate_group_user_directory_playbook()
        self.play_group_user_playbook()


    def generate_group_user_directory_playbook(self):
        (dryrun, logger, conf, util, tpl_vars) = (self.dryrun, self.logger, self.conf, self.util, self.tpl_vars)
        tasks = []
        # generate new part
        for r_name, r in conf['role'].items():
            tasks.append({
                'name': 'Ensure group "{}" exists'.format(r_name),
                'group': {
                    'name': r_name,
                    'state': 'present'
                }
            })
            tasks.append({
                'name': 'Ensure directory "{}" exists'.format(r['workspace']),
                'file': {
                    'path': r['workspace'],
                    'state': 'directory',
                    'mode': '0755',
                    'group': r_name,
                }
            })

            for u in r['user']:
                tasks.append({
                    'name': 'Ensure user "{}" exist, and belong to group "{}'"".format(u, r_name),
                    'user': {
                        'name': u,
                        'state': 'present',
                        'group': r_name,
                        'home': '{workspace}/{user}'.format(workspace=r['workspace'], user=u)
                    }
                })

        # generate deleted part
        for r_name in conf['diff_del']['group']:
            tasks.append({
                'name': 'Delete group "{}"'.format(r_name),
                'group': {
                    'name': r_name,
                    'state': 'absent'
                }
            })
        for r_name, r in conf['diff_del']['user'].items():
            for u in r['user']:
                tasks.append({
                    'name': 'Delete user "{}" '.format(u),
                    'user': {
                        'name': u,
                        'state': 'absent',
                        'remove': 'yes'
                    }
                })

        playbook = [{
            'name': 'Operating cluster hosts group, user, directory ...',
            'hosts': 'all',
            'user': 'root',
            'tasks': tasks
        }]
        util.mkdir(conf['ansible']['todo'])
        with open(conf['ansible']['todo'], 'w') as f:
            YAML().dump(playbook, f)


    def play_group_user_playbook(self):
        (dryrun, logger, conf, util, tpl_vars) = (self.dryrun, self.logger, self.conf, self.util, self.tpl_vars)
        ansible_cmd = 'ansible-playbook -i {inventory} {playbook}'.format(
            inventory=conf['ansible']['inventory'],
            playbook=conf['ansible']['todo']
        )
        logger.info(ansible_cmd)
        if dryrun:
            return
        ret = subprocess.call(ansible_cmd, shell=True)
        logger.debug(ret)
