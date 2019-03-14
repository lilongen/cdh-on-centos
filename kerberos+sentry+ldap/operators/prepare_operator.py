# coding: utf-8

import ldap
import re
import subprocess
from .base_operator import BaseOperator


class PrepareOperator(BaseOperator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.l: int

    @BaseOperator.cancel_on_error
    def execute(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        logger.info('PrepareOperator ...')
        logger.info('get valid AD user in specail group ...')
        self.bind_ldap()
        self.get_ldap_users()
        self.unbind_ldap()

        logger.info('get cluster host precense user and group info ...')
        self.get_node_user_group()

        logger.info('get diff between valid AD user and precense info  ...')
        self.get_presence_and_yaml_diff()

    def bind_ldap(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        ldap_conf = conf['ldap']
        l = ldap.initialize(ldap_conf['url'])
        l.simple_bind_s(ldap_conf['bind_dn'], ldap_conf['bind_pw'])
        self.l = l

    def unbind_ldap(self):
        self.l.unbind_s()

    def get_ldap_users(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        logger.info('get AD/ldap group users ...')
        l = self.l
        ldap_conf = conf['ldap']
        re_1st_ou = re.compile(r'CN=[^,]+,OU=([^,]+),')
        search_res = l.search(ldap_conf['base_dn'], ldap.SCOPE_SUBTREE, ldap_conf['filter'], ldap_conf['attrs'])
        users = []
        while True:
            result_type, result_data = l.result(search_res, 0)
            if (len(result_data) == 0):
                break
            result_type == ldap.RES_SEARCH_ENTRY and users.append(result_data)

        user_ids = []

        for entry in users:
            user_dn = entry[0][0]
            user_id = entry[0][1]['sAMAccountName'][0].decode()
            user_1stou = re.match(re_1st_ou, user_dn).group(1)
            user_ids.append(user_id)
        conf['group']['g_dev']['user'] = user_ids

    def get_node_user_group(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        result = subprocess.check_output("grep g_ /etc/group | awk -F: '{print $1}'", shell=True)
        groups = result.decode().split('\n')[0:-1]
        group_users = {}
        for g in groups:
            group_users[g] = {}
            result = subprocess.check_output('lid -n -g {}'.format(g), shell=True)
            users = result.decode().split('\n')[0:-1]
            group_users[g]['user'] = list(map(lambda x: re.sub('^\s+', '', x), users))

        conf['presence_role'] = group_users

    def get_presence_and_yaml_diff(self):
        var = self.var
        (dryrun, logger, conf, util, tpl_vars) = (var['dryrun'], var['logger'], var['conf'], var['util'], var['tpl_vars'])

        presence = conf['presence_role']
        definition = conf['group']
        diff = {
            'group': [],
            'user': {}
        }
        for pk, pv in presence.items():
            if definition.get(pk) is None:
                diff['group'].append(pk)
                diff['user'][pk] = pv
            else:
                diff['user'][pk] = {}
                diff['user'][pk]['user'] = set(pv['user']) - set(definition[pk]['user'])
        conf['diff_del'] = diff
        logger.debug(diff)
