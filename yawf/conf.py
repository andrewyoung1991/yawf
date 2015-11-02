"""
"""
from . import utils

__all__ = ("settings", "Settings")


class Settings(utils.Borg):
    """ settings are borg, they are one, they are always in sync in terms of
    attributes and methods.
    """
    def __init__(self, **kwargs):
        utils.Borg.__init__(self)
        for key, val in kwargs.items():
            setattr(self, key, val)


settings = utils.Frozen(Settings())
