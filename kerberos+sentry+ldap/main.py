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

from globals import gv
from util.utility import Utility
from operators.prepare_operator import PrepareOperator
from operators.ansible_operator import AnsibleOperator
from operators.hdfs_operator import HdfsOperator
from operators.kerberos_operator import KerberosOperator
from operators.distribute_keytab_operator import DistributeKeytabOperator


def init_ns(dryrun):
    gv.dryrun = dryrun
    gv.util = Utility()
    # required by following two lines
    gv.tpl_vars = {'cwd': os.path.dirname(sys.argv[0])}
    gv.logger = get_logger()
    gv.conf = get_conf()


def clean():
    gv.util.rm('./output')


def get_logger():
    with open('{cwd}/conf/logging.yml'.format(** gv.tpl_vars), 'r') as f:
        logging_config = YAML().load(f)
    dictConfig(logging_config)
    return logging.getLogger()


def get_conf():
    with open('{cwd}/conf/security.cdh.yml'.format(** gv.tpl_vars), 'r') as f:
        template = Template(f.read())
    return YAML().load(template.render(**gv.tpl_vars))


def get_enabled_operators(include, exclude):
    operators = [
        'PrepareOperator',
        'AnsibleOperator',
        'HdfsOperator',
        'KerberosOperator',
        'DistributeKeytabOperator'
    ]
    base = ['PrepareOperator']
    if include == '*':
        i = operators
    else:
        i = include.split(',')

    if exclude == '*':
        x = operators
    else:
        x = exclude.split(',')

    enabled =  set(base) | (set(i) - set(x))
    return list(filter(lambda i: i in enabled, operators))


@click.command()
@click.option('-d', '--dryrun', 'dryrun', type=bool, default=True, required=False)
@click.option('-i', '--include', 'include', type=str, default='*', required=False)
@click.option('-x', '--exclude', 'exclude', type=str, default='', required=False)
def main(dryrun, include, exclude):
    print('init app ...')

    init_ns(dryrun)
    clean()

    operators = get_enabled_operators(include, exclude)
    print(operators)
    for name in operators:
        globals()[name]().execute()


if __name__ == "__main__":
    main()
