# coding: utf-8

from abc import ABCMeta, abstractmethod


class BaseOperator(object, metaclass=ABCMeta):
    """
    Base class for functional operator to inherit.
    DO NOT use it directly!
    """

    err = 0

    def valid_kwargs(callable_):
        def wrapper(self, *args, **kwargs):
            if sorted(self.valid_keyword) != sorted(kwargs):
                print('{}.__init__(): missing needed kwarg'.format(type(self)))
                self.err = 1
            return callable_(self, *args, **kwargs)
        return wrapper

    def cancel_if_error(callable_):
        def wrapper(self, *args, **kwargs):
            if self.err == 0:
                return callable_(self, *args, **kwargs)
            else:
                class_ = type(self)
                print('{cls}.err = {err}, \n{cls}.execute() ... ignored'.format(cls=class_, err=self.err))
                return (lambda: None)()
        return wrapper

    #@valid_kwargs
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def execute(self) -> None:
        """
        :return: execute status code
        :rtype: None
        """
        raise NotImplementedError()
