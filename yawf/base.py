try:
    from abc import ABC
except ImportError:  # pragma: no cover
    # python 3.3
    from abc import ABCMeta
    class ABC(metaclass=ABCMeta):
        """a simple ABC that has ABCMeta as its metaclass"""

import asyncio


class BaseHandler(ABC):
    """ an abstract base class for handling websocket connections
    """
    __slots__ = ("websocket",)

    def __init__(self):
        self.websocket = None  # initialize websocket variable

    @asyncio.coroutine
    def __call__(self, ws, *args, **kwargs):
        self.websocket = ws
        yield from self.handle(*args, **kwargs)
        return ws

    @asyncio.coroutine
    def handle(self, *args, **kwargs):
        raise NotImplementedError

    def __str__(self):
        return "<{0} :: {1}>".format(self.__class__.__name__, self.websocket)
    __repr__ = __str__
