# coding: utf-8

from abc import ABCMeta, abstractmethod


class BaseOperator(object, metaclass=ABCMeta):
    """
    Base class for functional operator to inherit.
    DO NOT use it directly!
    """

    err = 0
    valid_keyword = (
        'dryrun',
        'logger',
        'conf',
        'util',
        'tpl_vars',
    )
    # dict object hold cross-operator consistent data needed by operator
    # it will be init by __init__
    var: dict

    def valid_kwargs(callable_):
        def wrapper(self, *args, **kwargs):
            if sorted(self.valid_keyword) != sorted(kwargs):
                print('{}.__init__(): missing needed kwarg'.format(type(self)))
                self.err = 1
            return callable_(self, *args, **kwargs)
        return wrapper

    def cancel_on_error(callable_):
        def wrapper(self, *args, **kwargs):
            class_ = type(self)
            if self.err == 0:
                return callable_(self, *args, **kwargs)
            else:
                print('{cls}.err = {err}, \n{cls}.execute() ... ignored'.format(cls=class_, err=self.err))
                return (lambda: None)()
        return wrapper

    @valid_kwargs
    @abstractmethod
    def __init__(self, **kwargs):
        self.var = kwargs

    @abstractmethod
    def execute(self) -> None:
        """
        :return: execute status code
        :rtype: None
        """
        raise NotImplementedError()
