# coding: utf-8

import ldap
import re
import subprocess
from .base_operator import BaseOperator
from globals import gv


class PrepareOperator(BaseOperator):
    """
    this operator mainly do followings:

    1. get all valid ldap user by filter and assign to conf[group][primary_mode][g_dev][member]
    2. all primary_mode groups members as the base user set, to valid user in supplementary group member
    3. get node os present user and group info
    4. construct diff.view (present) and (yaml definition) user and group data
    5. get user and group diff between present and yaml definition
    """

    # uid=1001(lile) gid=1002(g_dev) groups=1002(g_dev),1004(g_etl)
    id_name_pattern = r'\d+\((\w+)\)'
    re_id_name = re.compile(id_name_pattern)
    re_primary_group = re.compile(r'gid=' + id_name_pattern)
    re_supplementary_groups = re.compile(r'groups=([\w\(\)\,]+)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ldap_obj: object

    @BaseOperator.cancel_if_error
    def execute(self):
        gv.logger.info('PrepareOperator ...')
        gv.logger.info('get valid AD user in specail group ...')
        self.bind_ldap()
        self.get_ldap_users()
        self.unbind_ldap()
        self.valid_user_in_supplementary_group()

        gv.logger.info('get cluster host precense user and group info ...')
        self.get_present_user_and_group()
        self.get_diff_between_present_and_yaml()
        self.output_conf()

    def bind_ldap(self):
        ldap_conf = gv.conf['ldap']
        self.ldap_obj = ldap.initialize(ldap_conf['url'])
        self.ldap_obj.simple_bind_s(ldap_conf['bind_dn'], ldap_conf['bind_pw'])

    def unbind_ldap(self):
        self.ldap_obj.unbind_s()

    def get_ldap_users(self):
        gv.logger.info('get AD/ldap group users ...')
        ldap_conf = gv.conf['ldap']
        re_1st_ou = re.compile(r'CN=[^,]+,OU=([^,]+),')
        search_res = self.ldap_obj.search(ldap_conf['base_dn'], ldap.SCOPE_SUBTREE, ldap_conf['filter'], ldap_conf['attrs'])
        users = []
        while True:
            result_type, result_data = self.ldap_obj.result(search_res, 0)
            if (len(result_data) == 0):
                break
            result_type == ldap.RES_SEARCH_ENTRY and users.append(result_data)
        gv.logger.info(users)
        user_ids = []
        for entry in users:
            user_dn = entry[0][0]
            user_id = entry[0][1]['sAMAccountName'][0].decode()
            user_1stou = re.match(re_1st_ou, user_dn).group(1)
            user_ids.append(user_id)
        gv.conf['group']['primary_mode']['g_dev']['member'] = user_ids

    def valid_user_in_supplementary_group(self):
        valid_user = []
        for g_name, g in gv.conf['group']['primary_mode'].items():
            valid_user += g['member']

        valid_user_set = set(valid_user)
        for g_name, g in gv.conf['group']['supplementary_mode'].items():
            g['member'] = list(set(g['member']) & valid_user_set)

    def get_present_user_and_group(self):
        result = subprocess.check_output("grep g_ /etc/group | awk -F: '{print $1}'", shell=True)
        groups = result.decode().split('\n')[0:-1]
        group_users = {}
        for g in groups:
            group_users[g] = {}
            result = subprocess.check_output('lid -n -g {}'.format(g), shell=True)
            users = result.decode().split('\n')[0:-1]
            group_users[g]['member'] = list(map(lambda x: re.sub('^\s+', '', x), users))

        gv.conf['present_group'] = group_users

    def get_user_info(self, user):
        # uid=1001(lile) gid=1002(g_dev) groups=1002(g_dev),1004(g_etl)
        result = subprocess.check_output('id {user}'.format(user=user), shell=True)
        result = result.decode('utf-8')
        m_primary = self.re_primary_group.search(result)
        m_supplementary = self.re_supplementary_groups.search(result)
        primary = m_primary.group(1)
        supplementary_part = m_supplementary.group(1)
        supplementary = self.re_id_name.findall(supplementary_part)
        return {
            'primary': primary,
            'supplementary': supplementary
        }

    def get_diffview_present_user_and_group(self):
        present = gv.conf['present_group']
        present_group_set = set(present)
        present_users = []
        for g, g_data in present.items():
            present_users += g_data['member']
        present_user_set = set(present_users)

        d_present_user = {}
        for username in present_user_set:
            d_present_user[username] = self.get_user_info(username)
        return {
            'group': dict.fromkeys(present_group_set, 1),
            'user': d_present_user
        }

    def get_diffview_yaml_user_and_group(self):
        yaml_ = gv.conf['group']
        yaml_groups = {}
        d_yaml_user = {}
        for mode in yaml_:
            for g_name, g in yaml_[mode].items():
                yaml_groups[g_name] = 1
                for u_name in g['member']:
                    if d_yaml_user.get(u_name) is None:
                        d_yaml_user[u_name] = {
                            'primary': '',
                            'supplementary': []
                        }
                    if mode == 'primary_mode':
                        d_yaml_user[u_name]['primary'] = g_name
                    else:
                        d_yaml_user[u_name]['supplementary'].append(g_name)
        return {
            'group': yaml_groups,
            'user': d_yaml_user
        }

    def get_diff_between_present_and_yaml(self):
        present = self.get_diffview_present_user_and_group()
        yaml_ = self.get_diffview_yaml_user_and_group()
        diff = {
            'group': {
                'del': set(present['group']) - set(yaml_['group']),
                'add': set(yaml_['group']) - set(present['group']),
                'intersection': set(yaml_['group']) & set(present['group']),
                'union': set(yaml_['group']) | set(present['group'])
            },
            'user': {
                'del': set(present['user']) - set(yaml_['user']),
                'add': set(yaml_['user']) - set(present['user']),
                'intersection': set(yaml_['user']) & set(present['user']),
                'union': set(yaml_['user']) | set(present['user'])
            }
        }
        gv.conf['present_and_yaml_diff'] = diff
        gv.conf['yaml'] = yaml_
        gv.conf['present'] = present

    def output_conf(self):
        gv.util.dump_yaml_to_file(gv.conf, gv.conf['runtime']['conf'])
