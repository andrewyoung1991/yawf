try:
    from abc import ABC
except ImportError:  # pragma: no cover
    # python 3.3
    from abc import ABCMeta
    class ABC(metaclass=ABCMeta):
        """a simple ABC that has ABCMeta as its metaclass"""

import asyncio

from . import auth


class BaseHandler(ABC):
    """ an abstract base class for handling websocket connections
    """
    AUTH = auth.JWTTokenAuth()

    send_schema = None
    recv_schema = None

    __slots__ = ("websockets",)

    def __init__(self):
        self.websockets = set()  # initialize websockets variable

    def __str__(self):
        return "<{0} :: Clients={1}>".format(
            self.__class__.__name__, len(self.websockets))
    __repr__ = __str__

    def add_websocket(self, websocket):
        """ add a websocket to the set of connected clients
        """
        self.websockets.add(websocket)

    def remove_websocket(self, websocket):
        """ remove a websocket from the set of connected clients
        """
        try:
            self.websockets.remove(websocket)
        except KeyError:  # pragma: no cover
            pass

    @asyncio.coroutine
    def __call__(self, ws, **kwargs):
        self.add_websocket(ws)  # add this websocket to the set of connections
        yield from self.handle(ws, **kwargs)
        self.remove_websocket(ws)  # remove this websocket form the set
        return ws

    @asyncio.coroutine
    def handle(self, ws, **kwargs):
        raise NotImplementedError

    @classmethod
    def as_handler(cls):
        return cls().__call__
