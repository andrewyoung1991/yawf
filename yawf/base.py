import abc
import asyncio


class BaseHandler(abc.ABC):
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
