# coding: utf-8

from ruamel.yaml import YAML
import subprocess
from .base_operator import BaseOperator


class AnsibleOperator(BaseOperator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @BaseOperator.cancel_if_error
    def execute(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        logger.info('AnsibleOperator ...')
        logger.info('generate group, user, directory playbook ...')
        self.generate_group_user_directory_playbook()

        logger.info('play group, user, directory playbook ...')
        self.play_group_user_playbook()

    def generate_group_user_directory_playbook(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        tasks = []
        # generate new part
        for g_name, g in conf['group'].items():
            tasks.append({
                'name': 'Ensure group "{}" exists'.format(g_name),
                'group': {
                    'name': g_name,
                    'state': 'present'
                }
            })
            tasks.append({
                'name': 'Ensure directory "{}" exists'.format(g['workspace']),
                'file': {
                    'path': g['workspace'],
                    'state': 'directory',
                    'mode': '0755',
                    'group': g_name,
                }
            })

            for u in g['user']:
                tasks.append({
                    'name': 'Ensure user "{}" exist, and belong to group "{}'"".format(u, g_name),
                    'user': {
                        'name': u,
                        'state': 'present',
                        'group': g_name,
                        'home': '{workspace}/{user}'.format(workspace=g['workspace'], user=u)
                    }
                })

        # generate deleted part
        for g_name in conf['diff_del']['group']:
            tasks.append({
                'name': 'Delete group "{}"'.format(g_name),
                'group': {
                    'name': g_name,
                    'state': 'absent'
                }
            })
        for g_name, g in conf['diff_del']['user'].items():
            for u in g['user']:
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
        util.mkdir_p(conf['ansible']['todo'])
        with open(conf['ansible']['todo'], 'w') as f:
            YAML().dump(playbook, f)

    def play_group_user_playbook(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        ansible_cmd = 'ansible-playbook -i {inventory} {playbook}'.format(
            inventory=conf['ansible']['inventory'],
            playbook=conf['ansible']['todo']
        )
        logger.info(ansible_cmd)
        if dryrun:
            return
        ret = subprocess.call(ansible_cmd, shell=True)
        logger.debug(ret)
