# coding: utf-8

from ruamel.yaml import YAML
import subprocess
from .base_operator import BaseOperator
from globals import gv


class AnsibleOperator(BaseOperator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @BaseOperator.cancel_if_error
    def execute(self):
        gv.logger.info('AnsibleOperator ...')
        gv.logger.info('generate group, user, directory playbook ...')
        self.generate_group_user_directory_playbook()

        gv.logger.info('play group, user, directory playbook ...')
        self.play_group_user_playbook()

    def generate_group_user_directory_playbook(self):
        tasks = []
        # generate delete present user and group
        delete_group_tasks = []
        for g_name, g in gv.conf['present_group'].items():
            delete_group_tasks.append({
                'name': 'Delete group "{}"'.format(g_name),
                'group': {
                    'name': g_name,
                    'state': 'absent'
                }
            })

            for u in g['member']:
                tasks.append({
                    'name': 'Delete user "{}" '.format(u),
                    'user': {
                        'name': u,
                        'state': 'absent',
                        'remove': 'yes'
                    }
                })
        # delete group after all user deleted
        tasks += delete_group_tasks

        # generate yaml definition user and group
        for group_mode in gv.conf['group']:
            for g_name, g in gv.conf['group'][group_mode].items():
                tasks.append({
                    'name': 'Ensure group "{}" exists'.format(g_name),
                    'group': {
                        'name': g_name,
                        'state': 'present'
                    }
                })

                if g.get('os_home') is not None:
                    tasks.append({
                        'name': 'Ensure directory "{}" exists'.format(g['os_home']),
                        'file': {
                            'path': g['os_home'],
                            'state': 'directory',
                            'mode': '0755',
                            'group': g_name,
                        }
                    })

                for u in g['member']:
                    entry = {
                        'name': 'Ensure user "{}" exist, and belong to group "{}"'.format(u, g_name),
                        'user': {
                            'name': u,
                            'state': 'present',
                            'group': g_name,
                            'append': group_mode == 'supplementary_mode'
                        }
                    }
                    if g.get('os_home') is not None:
                        entry['user']['home'] = '{os_home}/{user}'.format(os_home=g['os_home'], user=u)
                    tasks.append(entry)

        playbook = [{
            'name': 'Operating cluster hosts group, user, directory ...',
            'hosts': gv.conf['ansible']['cdh_host_pattern'],
            'user': 'root',
            'tasks': tasks
        }]
        gv.util.mkdir_p(gv.conf['ansible']['todo'])
        with open(gv.conf['ansible']['todo'], 'w') as f:
            YAML().dump(playbook, f)

    def play_group_user_playbook(self):
        ansible_cmd = 'ansible-playbook -i {inventory} {playbook}'.format(
            inventory=gv.conf['ansible']['inventory'],
            playbook=gv.conf['ansible']['todo']
        )
        gv.logger.info(ansible_cmd)
        if gv.dryrun:
            return
        ret = subprocess.call(ansible_cmd, shell=True)
        gv.logger.debug(ret)
