import asyncio

from websockets.server import WebSocketServerProtocol

from yawf.utils import get_app


class WebSocket(WebSocketServerProtocol):
    @asyncio.coroutine
    def recv(self):
        message = yield from super().recv()
        if message:
            app = get_app()
            message = app.run_middlewares(message, on="recv")
            return message

    @asyncio.coroutine
    def send(self, data):
        app = get_app()
        data = app.run_middlewares(message, "send")
        yield from super().send(data)
