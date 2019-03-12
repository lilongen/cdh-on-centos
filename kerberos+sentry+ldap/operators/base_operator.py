# coding: utf-8

from abc import ABCMeta, abstractmethod


class BaseOperator(object, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, **kwargs):
        self.var = kwargs

    @abstractmethod
    def execute(self):
        """
        :return: execute status code
        :rtype: int
        """
        raise NotImplementedError()
