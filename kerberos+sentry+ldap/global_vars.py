#!/usr/bin/env python
# coding: utf-8
#

from argparse import Namespace

gv = Namespace(**{
    'dryrun': bool,
    'logger': object,
    'conf': object,
    'util': object,
    'tpl_vars': object
})