import functools as ft


class Borg:
    """ a super Borg class where any instance of the class updates all instances
    """
    __shared_state__ = {}

    def __init__(self):
        self.__dict__ = self.__shared_state__

    def __str__(self):
        return str(self.__dict__)
    __repr__ = __str__

    def __getitem__(self, item):
        return super().__getattribute__(item)

    def __setitem__(self, item, value):
        return super().__setattr__(item, value)


class Frozen:
    """
    """
    class FrozenObjectError(Exception):
        """ exception to raise when a client attempts to change an attribute of
        a frozen object.
        """

    def __init__(self, instance):
        self._instance = instance

    def __getattribute__(self, key):
        if key == "_instance":
            return super(Frozen, self).__getattribute__(key)
        instance = getattr(self, "_instance")
        return instance.__getattribute__(key)

    def __setattr__(self, key, value):
        if key == "_instance":
            return super(Frozen, self).__setattr__(key, value)
        raise type(self).FrozenObjectError("cannot set attributes of a"
            " frozen object")
    __setitem__ = __setattr__


def singleton(*, update=False):
    def inner(klass):
        @ft.wraps(klass)
        def wrapper(*args, **kwargs):
            instance = getattr(klass, "_instance", None)
            if instance is None:
                instance = klass(*args, **kwargs)
                setattr(klass, "_instance", instance)
            if update is True:
                instance.__dict__.update(kwargs)
            return instance
        return wrapper
    return inner
