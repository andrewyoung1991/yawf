"""
.. module:: yawf.conf
.. module-author:: Andrew Young ayoung@thewulf.org
"""
import functools as ft
import os
import binascii

from . import utils

__all__ = ("settings", "Settings", "make_setting")


class Settings(utils.Borg):
    """ The Settings object is exactly what it sounds like. Its function is
    to operate as a key value store that can be accessed anywhere in your app.
    Settings should be considered fragile, and they should not be changed under
    any circumstance during runtime. To prevent this kind of mistake, import
    the frozen settings object from this module at runtime.

    .. code-block:: python
        :caption: app.py

        from yawf.conf import settings

    the frozen settings object will raise a `FrozenObjectError` if any of it's
    values are changed at runtime.

    .. code-block:: python
        :caption: app.py

        from yawf.conf import settings

        settings.foo = "bar"
        ---------------------------------------------------------------
        Exception
        ...
        ----> settings.foo = "bar"

        FrozenObjectError: cannot set attributes of a frozen object

    there is one special setting, `secret_key`, which will be generated at
    runtime for you. this is probably not what you are looking for if you will
    be encrypting values with your secret key. to persist your secret key add
    a value to `Settings.__lazy_secret_key` in your settings configuration.

    .. code-block:: python
        :caption: settings.py

        from yawf import Settings

        s = Settings()
        s.__lazy_secret_key = "d0n't-3@t-sn0w"

    now in another module you can check that it has persisted

    .. code-block:: bash
        $ yawf shell
        Python 3.5.0 (default, Oct 12 2015, 16:28:55)
        [GCC 4.9.2] on linux
        Type "help", "copyright", "credits" or "license" for more information.
        >>> from yawf.conf import settings
        >>> print(settings.secret_key)
        ... "d0n't-3@t-sn0w"
    """
    def __init__(self, **kwargs):
        utils.Borg.__init__(self)
        for key, val in kwargs.items():
            setattr(self, key, val)  # pragma: no cover

    def __str__(self):
        return dict.__str__(self)
    __repr__ = __str__

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
