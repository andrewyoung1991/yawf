import asyncio
from datetime import datetime

from yawf.compatibility import yayson
from .middleware import Middleware


class JSONMiddleware(Middleware):
    """
    - load all recieved messages as json
    - dump all sent messages as json
    """

    @asyncio.coroutine
    def on_send(self, message):
        message = yayson.dumps(message)
        return message

    @asyncio.coroutine
    def on_recv(self, message):
        message = yayson.loads(message)
        return message
