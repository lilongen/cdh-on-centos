#!/usr/bin/env python
# coding: utf-8
#

from __future__ import absolute_import
from ruamel.yaml import YAML
import sys
import os
import logging
from jinja2 import Template
from logging.config import dictConfig
from util.utility import Utility
from operators.prepare_operator import PrepareOperator
from operators.ansible_operator import AnsibleOperator
from operators.hdfs_operator import HdfsOperator
from operators.kerberos_operator import KerberosOperator
from operators.distribute_keytab_operator import DistributeKeytabOperator


dryrun = True

logger: logging.Logger
conf: dict
l: int
util = Utility()
tpl_vars = {'cwd': os.path.dirname(sys.argv[0])}


def init_logger():
    global logger
    logging_config: dict
    with open('{cwd}/conf/logging.yml'.format(**tpl_vars), 'r') as f:
        logging_config = YAML().load(f)
    dictConfig(logging_config)
    logger = logging.getLogger()


def get_conf():
    global conf, l
    with open('{cwd}/conf/security.cdh.yml'.format(**tpl_vars), 'r') as f:
        template = Template(f.read())
        conf = YAML().load(template.render(**tpl_vars))



def main():
    print('init app ...')
    init_logger()
    get_conf()
    PrepareOperator(dryrun, logger, conf, util, tpl_vars).execute()
    AnsibleOperator(dryrun, logger, conf, util, tpl_vars).execute()
    HdfsOperator(dryrun, logger, conf, util, tpl_vars).execute()
    KerberosOperator(dryrun, logger, conf, util, tpl_vars).execute()
    DistributeKeytabOperator(dryrun, logger, conf, util, tpl_vars).execute()

    logger.info('get AD/ldap group users ...')


if __name__ == "__main__":
    main()
