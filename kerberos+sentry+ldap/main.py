#!/usr/bin/env python
# coding: utf-8
#

import sys
import os
import logging

from ruamel.yaml import YAML
from jinja2 import Template
from logging.config import dictConfig
import click

from util.utility import Utility
from operators.prepare_operator import PrepareOperator
from operators.ansible_operator import AnsibleOperator
from operators.hdfs_operator import HdfsOperator
from operators.kerberos_operator import KerberosOperator
from operators.distribute_keytab_operator import DistributeKeytabOperator


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


@click.command()
@click.option('-d', '--dryrun', 'dryrun', type=bool, default=True, required=False)
@click.option('-f', '--filter', 'filter', type=str, default='*', required=False)
def main(dryrun, filter):
    print('init app ...')

    init_logger()
    get_conf()

    operator_kwargs = {
        'dryrun': dryrun,
        'logger': logger,
        'conf': conf,
        'util': util,
        'tpl_vars': tpl_vars
    }
    operators = (
        'PrepareOperator',
        'AnsibleOperator',
        'HdfsOperator',
        'KerberosOperator',
        'DistributeKeytabOperator',
    )
    filter = filter.split(',')
    for name in operators:
        if name == 'PrepareOperator' \
            or '*' in filter \
            or name in filter:
            globals()[name](**operator_kwargs).execute()


if __name__ == "__main__":
    main()
