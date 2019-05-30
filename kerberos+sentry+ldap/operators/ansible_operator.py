# coding: utf-8

import subprocess
from .base_operator import BaseOperator
from globals import gv


class AnsibleOperator(BaseOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @BaseOperator.cancel_if_error
    def execute(self):
        gv.logger.info('AnsibleOperator ...')
        gv.logger.info('generate group, user, directory playbook ...')
        self.generate_playbook_remove_then_recreate()
        self.generate_playbook_using_diff()
        gv.logger.info('play group, user, directory playbook ...')
        self.play_playbook_remove_then_recreate()

    def get_group_os_home(self, g):
        if gv.conf['group']['primary_mode'].get(g) is not None:
            return gv.conf['group']['primary_mode'][g]['os_home']
        else:
            return None

    def generate_playbook_using_diff(self):
        tasks = []
        diff = gv.conf['present_and_yaml_diff']
        for u in diff['user']['del']:
            tasks.append({
                'name': 'Delete user "{}" '.format(u),
                'user': {
                    'name': u,
                    'state': 'absent',
                    'remove': 'yes'
                }
            })
        for g_name in diff['group']['del']:
            tasks.append({
                'name': 'Delete group "{}"'.format(g_name),
                'group': {
                    'name': g_name,
                    'state': 'absent'
                }
            })
        for g_name in diff['group']['intersection'] | diff['group']['add']:
            tasks.append({
                'name': 'Ensure group "{}" exists'.format(g_name),
                'group': {
                    'name': g_name,
                    'state': 'present'
                }
            })

            group_os_home = self.get_group_os_home(g_name)
            if group_os_home is not None:
                tasks.append({
                    'name': 'Ensure directory "{}" exists'.format(group_os_home),
                    'file': {
                        'path': group_os_home,
                        'state': 'directory',
                        'mode': '0755',
                        'group': g_name,
                    }
                })

        for u in diff['user']['intersection'] | diff['user']['add']:
            yaml_user = gv.conf['yaml']['user'][u]
            user_primary_group = yaml_user['primary']
            user_supplementary_groups = yaml_user['supplementary']
            user_supplementary_groups = gv.util.list_remove_item(user_supplementary_groups, user_primary_group)
            os_home = gv.conf['group']['primary_mode'][user_primary_group]['os_home']
            home = '{os_home}/{user}'.format(os_home=os_home, user=u)
            entry = {
                'name': 'Ensure user "{}" exist, and belong to group "{}"'.format(u, user_primary_group),
                'user': {
                    'name': u,
                    'state': 'present',
                    'home': home,
                    'group': user_primary_group,
                    'groups': user_supplementary_groups,
                    'append': False
                }
            }
            tasks.append(entry)

        self.output_playbook(tasks, gv.conf['ansible']['todo_diff'])

    def generate_playbook_remove_then_recreate(self):
        tasks = []
        # generate delete present user and group
        delete_group_tasks = []
        users = {}
        for g_name, g in gv.conf['present_group'].items():
            delete_group_tasks.append({
                'name': 'Delete group "{}"'.format(g_name),
                'group': {
                    'name': g_name,
                    'state': 'absent'
                }
            })

            for u in g['member']:
                if users.get(u) is None:
                    users[u] = 1
                else:
                    continue
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
                            'append': group_mode == 'supplementary_mode'
                        }
                    }
                    if group_mode == 'primary_mode':
                        if g.get('os_home') is not None:
                            entry['user']['home'] = '{os_home}/{user}'.format(os_home=g['os_home'], user=u)
                        entry['user']['group'] = g_name
                    else:
                        entry['user']['groups'] = [g_name]
                    tasks.append(entry)

        self.output_playbook(tasks, gv.conf['ansible']['todo'])

    def output_playbook(self, tasks, file):
        playbook = [{
            'name': 'Operating cluster hosts group, user, directory ...',
            'hosts': gv.conf['ansible']['cdh_host_pattern'],
            'user': 'root',
            'tasks': tasks
        }]
        gv.util.dump_yaml_to_file(playbook, file)

    def play_playbook_remove_then_recreate(self):
        self.play_playbook(gv.conf['ansible']['todo'])

    def play_playbook_diff(self):
        self.play_playbook(gv.conf['ansible']['todo_diff'])

    def play_playbook(self, playbook):
        ansible_cmd = 'ansible-playbook -i {inventory} {playbook}'.format(
            inventory=gv.conf['ansible']['inventory'],
            playbook=playbook
        )
        gv.logger.info(ansible_cmd)
        if gv.dryrun:
            return
        ret = subprocess.call(ansible_cmd, shell=True)
        gv.logger.debug(ret)
