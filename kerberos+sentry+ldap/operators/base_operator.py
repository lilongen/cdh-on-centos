# coding: utf-8

from abc import ABCMeta, abstractmethod


class BaseOperator(object, metaclass=ABCMeta):
    """
    Base class for functional operator to inherit.
    DO NOT use it directly!
    """

    err = 0

    def valid_gv(callable_):
        def wrapper(self, *args, **kwargs):
            self.err = 0
            return callable_(self, *args, **kwargs)
        return wrapper

    def cancel_on_error(callable_):
        def wrapper(self, *args, **kwargs):
            if self.err == 0:
                return callable_(self, *args, **kwargs)
            else:
                class_ = type(self)
                print('{cls}.err = {err}, \n{cls}.execute() ... ignored'.format(cls=class_, err=self.err))
                return (lambda: None)()
        return wrapper

    @valid_gv
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self) -> None:
        """
        :return: execute status code
        :rtype: None
        """
        raise NotImplementedError()
