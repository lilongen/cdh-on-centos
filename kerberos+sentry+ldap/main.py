#!/usr/bin/env python
# coding: utf-8
#

from ruamel.yaml import YAML
import ldap
import re
import subprocess
import sys
import os
from jinja2 import Template
import logging
from logging.config import dictConfig
from util.mailer import Mailer

logger: object
conf: dict
l: int

yml_vars = {
    'cwd': os.path.dirname(sys.argv[0])
}

def init_logger():
    global logger
    logging_config: dict
    with open('{cwd}/conf/logging.yml'.format(**yml_vars), 'r') as f:
        logging_config = YAML().load(f)
    dictConfig(logging_config)
    logger = logging.getLogger()


def get_conf():
    global conf, l
    with open('{cwd}/conf/security.cdh.yml'.format(**yml_vars), 'r') as f:
        template = Template(f.read())
        conf = YAML().load(template.render(**yml_vars))


def bind_ldap():
    global conf, l
    ldap_conf = conf['ldap']
    l = ldap.initialize(ldap_conf['url'])
    l.simple_bind_s(ldap_conf['bind_dn'], ldap_conf['bind_pw'])


def unbind_ldap():
    global conf, l
    l.unbind_s()


def get_ldap_users():
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
    conf['role']['g_dev']['user'] = user_ids


def generate_group_user_directory_playbook():
    playbook = []
    #generate new part
    for r_name, r in conf['role'].items():
        playbook.append({
            'name': 'Ensure group "{}" exists'.format(r_name),
            'group': {
                'name': r_name,
                'state': 'present'
            }
        })
        playbook.append({
            'name': 'Ensure directory "{}" exists'.format(r['workspace']),
            'file': {
                'path': r['workspace'],
                'state': 'directory',
                'mode': '0755',
                'group': r_name,
            }
        })

        for u in r['user']:
            playbook.append({
                'name': 'User "{}" info'.format(u),
                'user': {
                    'name': u,
                    'state': 'present',
                    'group': r_name
                }
            })
            
    #generate deleted part
    for r_name in conf['diff_del']['group']:
        playbook.append({
            'name': 'Delete group "{}"'.format(r_name),
            'group': {
                'name': r_name,
                'state': 'absent'
            }
        })
    for r_name, r in conf['diff_del']['user'].items():
        for u in r['user']:
            playbook.append({
                'name': 'Delete user "{}" '.format(u),
                'user': {
                    'name': u,
                    'state': 'absent'
                }
            })
            
    #persist to file
    with open('{}/main.yml'.format(conf['ansible']['role_main_yml_to']), 'w') as f: YAML().dump(playbook, f)


def get_presence_and_yaml_diff():
    presence = conf['presence_role']
    definition = conf['role']
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


def operate_principle():
    kadmin_with_credential = 'kadmin -p {admin} -w {admin_pw} '
    addprinc_tpl = kadmin_with_credential + 'addprinc -pw lle {username}'
    ktadd_tpl = kadmin_with_credential + 'ktadd -k {keytab_to}/{username}.keytab {username}'
    delprinc_tpl = kadmin_with_credential + 'delprinc -force {username}'
    cmds = ''
    vars = conf['kerberos']
    for r_name, r in conf['role'].items():
        for u in r['user']:
            vars['username'] = u
            cmds += addprinc_tpl.format(**vars) + '\n'
            cmds += ktadd_tpl.format(**vars) + '\n'
    for r_name, r in conf['diff_del']['user'].items():
        logger.debug(r'user')
        for u in r['user']:
            vars['username'] = u
            cmds += delprinc_tpl.format(**vars) + '\n'

    sh = '{}/add.or.del.principle.sh'.format(conf['kerberos']['keytab_to'])
    with open(sh, 'w') as f:
        f.write(cmds)
    ret = subprocess.call('bash {}'.format(sh), shell=True)
    logger.debug(ret)


def get_node_user_group():
    result = subprocess.check_output("grep g_ /etc/group | awk -F: '{print $1}'", shell=True)
    groups = result.decode().split('\n')[0:-1]
    group_users = {}
    for g in groups:
        group_users[g] = {}
        result = subprocess.check_output('lid -n -g {}'.format(g), shell=True)
        users = result.decode().split('\n')[0:-1]
        group_users[g]['user'] = list(map(lambda x: re.sub('^\s+', '', x), users))
    
    conf['presence_role'] = group_users

def distribute_keytab():
    mailer = Mailer()
    user_keytab = {}
    for r_name, r in conf['role'].items():
        for username in r['user']:
            user_keytab[username] = '{}/{}.keytab'.format(conf['kerberos']['keytab_to'], username)

    f_tpl = open('{cwd}/conf/mailtpl.keytab.distribute.yml'.format(**yml_vars), 'r')
    tpl = f_tpl.read()
    f_tpl.close()
    for username, keytab in user_keytab.items():
        if username != 'lile':
            continue

        yml_vars['name'] = username
        mail = YAML().load(Template(tpl).render(**yml_vars))
        mail['to'] = '%s@yxt.com' % username
        mail['files'] = [keytab]
        logger.info('Mail {}.keytab to {} ...'.format(username, mail['to']))
        mailer.send([mail['to']], mail)


def main():
    init_logger()
    get_conf()

    bind_ldap()
    get_ldap_users()
    unbind_ldap()

    distribute_keytab()
    return

    get_node_user_group()
    get_presence_and_yaml_diff()
    generate_group_user_directory_playbook()
    operate_principle()



if __name__ == "__main__":
    main()
