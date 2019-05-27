# coding: utf-8

import ldap
import re
import subprocess
from .base_operator import BaseOperator
from ns import ns


class PrepareOperator(BaseOperator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ldap_obj: object

    @BaseOperator.cancel_if_error
    def execute(self):
        ns.logger.info('PrepareOperator ...')
        ns.logger.info('get valid AD user in specail group ...')
        self.bind_ldap()
        self.get_ldap_users()
        self.unbind_ldap()

        ns.logger.info('get cluster host precense user and group info ...')
        self.get_node_user_group()

    def bind_ldap(self):
        ldap_conf = ns.conf['ldap']
        self.ldap_obj = ldap.initialize(ldap_conf['url'])
        self.ldap_obj.simple_bind_s(ldap_conf['bind_dn'], ldap_conf['bind_pw'])

    def unbind_ldap(self):
        self.ldap_obj.unbind_s()

    def get_ldap_users(self):
        ns.logger.info('get AD/ldap group users ...')
        ldap_conf = ns.conf['ldap']
        re_1st_ou = re.compile(r'CN=[^,]+,OU=([^,]+),')
        search_res = self.ldap_obj.search(ldap_conf['base_dn'], ldap.SCOPE_SUBTREE, ldap_conf['filter'], ldap_conf['attrs'])
        users = []
        while True:
            result_type, result_data = self.ldap_obj.result(search_res, 0)
            if (len(result_data) == 0):
                break
            result_type == ldap.RES_SEARCH_ENTRY and users.append(result_data)

        user_ids = []

        for entry in users:
            user_dn = entry[0][0]
            user_id = entry[0][1]['sAMAccountName'][0].decode()
            user_1stou = re.match(re_1st_ou, user_dn).group(1)
            user_ids.append(user_id)
        ns.conf['group']['primary_mode']['g_dev']['member'] = user_ids

    def get_node_user_group(self):
        result = subprocess.check_output("grep g_ /etc/group | awk -F: '{print $1}'", shell=True)
        groups = result.decode().split('\n')[0:-1]
        group_users = {}
        for g in groups:
            group_users[g] = {}
            result = subprocess.check_output('lid -n -g {}'.format(g), shell=True)
            users = result.decode().split('\n')[0:-1]
            group_users[g]['member'] = list(map(lambda x: re.sub('^\s+', '', x), users))

        ns.conf['present_group'] = group_users
