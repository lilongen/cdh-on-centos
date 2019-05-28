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

from global_vars import gv
from util.utility import Utility
from operators.prepare_operator import PrepareOperator
from operators.ansible_operator import AnsibleOperator
from operators.hdfs_operator import HdfsOperator
from operators.kerberos_operator import KerberosOperator
from operators.distribute_keytab_operator import DistributeKeytabOperator


def get_logger():
    with open('{cwd}/conf/logging.yml'.format(** gv.tpl_vars), 'r') as f:
        logging_config = YAML().load(f)
    dictConfig(logging_config)
    return logging.getLogger()


def get_conf():
    with open('{cwd}/conf/security.cdh.yml'.format(** gv.tpl_vars), 'r') as f:
        template = Template(f.read())
    return YAML().load(template.render(**gv.tpl_vars))


def init_ns(dryrun):
    gv.dryrun = dryrun
    gv.util = Utility()
    # required by following two lines
    gv.tpl_vars = {'cwd': os.path.dirname(sys.argv[0])}
    gv.logger = get_logger()
    gv.conf = get_conf()


@click.command()
@click.option('-d', '--dryrun', 'dryrun', type=bool, default=True, required=False)
@click.option('-f', '--filter', 'filter', type=str, default='*', required=False)
def main(dryrun, filter):
    print('init app ...')

    init_ns(dryrun)
    enabled_list = ['PrepareOperator'] + filter.split(',')

    operators = (
        'PrepareOperator',
        'AnsibleOperator',
        'HdfsOperator',
        'KerberosOperator',
        'DistributeKeytabOperator',
    )
    for name in operators:
        if '*' in filter or name in enabled_list:
            globals()[name]().execute()


if __name__ == "__main__":
    main()
