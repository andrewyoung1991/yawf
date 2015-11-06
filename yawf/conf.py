"""
"""
import functools as ft
import os
import binascii

from . import utils

__all__ = ("settings", "Settings", "make_setting")


class Settings(utils.Borg):
    """ settings are borg, they are one, they are always in sync in terms of
    attributes and methods.
    """
    def __init__(self, **kwargs):
        utils.Borg.__init__(self)
        for key, val in kwargs.items():
            setattr(self, key, val)  # pragma: no cover

    @utils.lazyprop
    def secret_key(self):
        return binascii.hexlify(os.urandom(24)).decode()

    def get(self, key, default=None):
        return getattr(self, key, default)


settings = utils.Frozen(Settings())


def make_setting(key, value):
    """ if you really need to alter your runtime settings (maybe for testing
    this is okay, but otherwise don't do it).
    """
    s = Settings()
    setattr(s, key, value)
    return s


def patch_settings(**kwargs):
    """ decorate a function, altering settings for the duration of its call.
    """
    cached = {}

    def _set():
        for key, value in kwargs.items():
            cached[key] = settings.get(key)
            make_setting(key, value)

    def _reset():
        for key, value in cached.items():
            make_setting(key, value)

    def inner(fn):
        @ft.wraps(fn)
        def wrapper(*args, **kwargs):
            _set()
            err = None
            try:
                results = fn(*args, **kwargs)
            except Exception as e:
                err = e
            _reset()
            if isinstance(err, Exception):
                raise err
            return results
        return wrapper
    return inner
