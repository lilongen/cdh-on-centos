# coding: utf-8

from abc import ABCMeta, abstractmethod


class Operator(object):
    __metaclass__ = ABCMeta

    @property
    def name(self):
        """
        :return: the operator name
        :rtype: unicode
        """
        raise NotImplementedError()

    @abstractmethod
    def execute(self):
        """
        :return: execute status code
        :rtype: int
        """
        raise NotImplementedError()
