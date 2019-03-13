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
from operators.prepare_operator import PrepareOperator
from operators.ansible_operator import AnsibleOperator
from operators.hdfs_operator import HdfsOperator
from operators.kerberos_operator import KerberosOperator
from operators.distribute_keytab_operator import DistributeKeytabOperator


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


def main():
    print('init app ...')
    init_logger()
    get_conf()

    operator_var = {
        'dryrun': dryrun,
        'logger': logger,
        'conf': conf,
        'util': util,
        'tpl_vars': tpl_vars
    }

    PrepareOperator(**operator_var).execute()
    AnsibleOperator(**operator_var).execute()
    HdfsOperator(**operator_var).execute()
    KerberosOperator(**operator_var).execute()
    DistributeKeytabOperator(**operator_var).execute()


if __name__ == "__main__":
    main()
