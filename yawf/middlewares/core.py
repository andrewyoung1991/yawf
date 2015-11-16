import asyncio
from datetime import datetime

from yawf.compatibility import yayson
from yawf.auth import JWTTokenAuth
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


class JWTMiddleware(Middleware):
    """ relies on JSONMiddleware
    """
    validator = JWTTokenAuth()

    @asyncio.coroutine
    def on_recv(self, message):
        auth_user = message.pop("authentication", None)
        if auth_user:
            auth_user = self.validator.validate(auth_user)
        message["auth_user"] = auth_user
        return message

    @asyncio.coroutine
    def on_send(self, message):
        message.pop("auth_user", None)
        return message
