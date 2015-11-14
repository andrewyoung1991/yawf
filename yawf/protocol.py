import asyncio

from websockets.server import WebSocketServerProtocol

from yawf.utils import get_app


class WebSocket(WebSocketServerProtocol):
    @asyncio.coroutine
    def recv(self):
        message = yield from super().recv()
        if message:
            app = get_app()
            message = yield from app.run_middlewares(message, on="recv")
            return message

    @asyncio.coroutine
    def send(self, message):
        app = get_app()
        data = yield from app.run_middlewares(message, on="send")
        yield from super().send(data)
