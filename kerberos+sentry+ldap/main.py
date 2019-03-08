#!/usr/bin/env python
# coding: utf-8
#

from ruamel.yaml import YAML
import ldap
import re
import subprocess
import sys
import os
import logging
from jinja2 import Template
from logging.config import dictConfig
from util.mailer import Mailer
from util.utility import Utility


Dryrun = len(sys.argv) > 1 and str(sys.argv[1]).lower() == 'dryrun'

logger: object
conf: dict
l: int
util = Utility()

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


def generate_group_user_directory_playbook():
    tasks = []
    #generate new part
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
            
    #generate deleted part
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


def play_group_user_playbook():
    ansible_cmd = 'ansible-playbook -i {inventory} {playbook}'.format(
        inventory=conf['ansible']['inventory'],
        playbook=conf['ansible']['todo']
    )
    logger.info(ansible_cmd)
    if Dryrun:
        return
    ret = subprocess.call(ansible_cmd, shell=True)
    logger.debug(ret)


def set_role_hdfs_workspace():
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
    if Dryrun:
        return
    subprocess.call('bash %s' % sh, shell=True)


def operate_principle():
    kadmin_with_credential = 'kadmin -p {admin} -w {admin_pw} '
    addprinc_tpl = kadmin_with_credential + 'addprinc -pw lle {username}'
    ktadd_tpl = kadmin_with_credential + 'ktadd -k {keytab_output_to}/{username}.keytab {username}'
    delprinc_tpl = kadmin_with_credential + 'delprinc -force {username}'
    cmds = ''
    vars = conf['kerberos']
    for r_name, r in conf['role'].items():
        for u in r['user']:
            vars['username'] = u
            cmds += addprinc_tpl.format(**vars) + '\n'
            cmds += ktadd_tpl.format(**vars) + '\n'
    for r_name, r in conf['diff_del']['user'].items():
        for u in r['user']:
            vars['username'] = u
            cmds += delprinc_tpl.format(**vars) + '\n'

    util.mkdir(conf['kerberos']['todo'])
    sh = conf['kerberos']['todo']
    with open(sh, 'w') as f:
        f.write(cmds)

    if Dryrun:
        return
    ret = subprocess.call('bash {}'.format(sh), shell=True)
    logger.info(ret)


def distribute_keytab():
    info = conf['mail']
    mailer = Mailer(server=info['server'],
                    sender=info['sender'],
                    username=info['username'],
                    password=info['password'])
    user_keytab = {}
    for r_name, r in conf['role'].items():
        for username in r['user']:
            user_keytab[username] = '{}/{}.keytab'.format(conf['kerberos']['keytab_output_to'], username)

    f_tpl = open('{cwd}/conf/mail.keytab.distribute.tpl.yml'.format(**yml_vars), 'r')
    tpl = f_tpl.read()
    f_tpl.close()
    for username, keytab in user_keytab.items():
        yml_vars['name'] = username
        yml_vars['kerberos_realm'] = conf['kerberos']['realm']
        mail = YAML().load(Template(tpl).render(**yml_vars))
        mail['to'] = '%s@yxt.com' % username
        mail['files'] = [keytab]
        logger.info('mail {}.keytab file to {} ...'.format(username, mail['to']))
        if Dryrun:
            continue
        mailer.send([mail['to']], mail)


def main():
    print('init app ...')
    init_logger()
    get_conf()

    logger.info('get valid ldap group users ...')
    bind_ldap()
    get_ldap_users()
    unbind_ldap()

    logger.info('get cluster presence group and user information ...')
    get_node_user_group()
    get_presence_and_yaml_diff()

    logger.info('generate user/group playbook ...')
    generate_group_user_directory_playbook()

    logger.info('run playbook ... ')
    play_group_user_playbook()

    logger.info('operate role hdfs directory ...')
    set_role_hdfs_workspace()

    logger.info('operate kerberos principle ...')
    operate_principle()

    logger.info('distribute user keytab ...')
    distribute_keytab()


if __name__ == "__main__":
    main()
