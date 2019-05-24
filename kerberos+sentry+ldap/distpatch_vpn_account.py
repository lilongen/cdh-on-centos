#!/usr/bin/env python
# coding: utf-8
#

import sys
import os
import logging

from ruamel.yaml import YAML
from jinja2 import Template
from logging.config import dictConfig

from util.utility import Utility
from util.mailer import Mailer
import zipfile2



dryrun = len(sys.argv) > 1 and str(sys.argv[1]).lower() == 'dryrun'

logger: logging.Logger
conf: dict
util = Utility()
tpl_vars = {'cwd': os.path.dirname(sys.argv[0])}


def init_logger():
    global logger
    with open('{cwd}/conf/logging.yml'.format(**tpl_vars), 'r') as f:
        logging_config = YAML().load(f)
    dictConfig(logging_config)
    logger = logging.getLogger()


def get_conf():
    global conf
    with open('{cwd}/conf/security.cdh.yml'.format(**tpl_vars), 'r') as f:
        template = Template(f.read())
    conf = YAML().load(template.render(**tpl_vars))


def generate_user_pack(username):
    files = [
        '%s.crt' % username,
        '%s.key' % username,
        './config/ca.crt',
        './config/ta.key',
        './config/client.ovpn'
    ]
    zf = zipfile2.ZipFile('%s.zip' % username, 'w')
    for f in files:
        try:
            zf.write(f)
        except Exception as e:
            logger.error(e)
            logger.error('add %s error ...' %f)
            zf.close()
            return False

    zf.close()
    return True


def main():
    print('init app ...')
    init_logger()
    get_conf()

    info = conf['mail']
    mailer = Mailer(
        server=info['server'],
        sender=info['sender'],
        username=info['username'],
        password=info['password']
    )

    with open('{cwd}/conf/mail.vpn.account.tpl.yml'.format(**tpl_vars), 'r') as f_tpl:
        tpl = f_tpl.read()

    vpn_account_key_crt_location = '/Users/lilongen/onedrive/new.vpn.account'
    os.chdir(vpn_account_key_crt_location)
    suzhou = ['lile', 'luoyw', 'baosy', 'liukl', 'tangzx', 'wangxt', 'jingwz', 'yujun', 'suxj', 'yangwb', 'yyc', 'maocy', 'xuxt']
    nanjing = ['liuzl', 'wanglj', 'guoqp', 'liuc', 'sunxf']
    users = suzhou + nanjing
    # users = ['lile']
    for username in users:
        tpl_vars['name'] = username
        mail = YAML().load(Template(tpl).render(**tpl_vars))
        mail['to'] = '%s@yxt.com' % username
        ret = generate_user_pack(username)
        if not ret:
            continue

        mail['files'] = ['%s.zip' % username]
        logger.info('mail {} vpn account files to {} ...'.format(username, mail['to']))
        if dryrun:
            continue
        mailer.send([mail['to']], mail)

if __name__ == "__main__":
    main()
