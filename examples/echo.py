import asyncio

import websockets

from yawf import App, Handler


app = App(name="test")

@app.route("/echo")
class Echo(Handler):
    @asyncio.coroutine
    def handle(self, *args, **kwargs):
        app.logger.debug("recieved a websocket connection")
        while self.websocket.open:
            app.logger.debug("websocket.open {}".format(self.websocket.open))
            app.logger.debug("waiting for value from client")
            value = yield from self.websocket.recv()
            if value is None:
                break
            app.logger.debug("recieved `{}` from client".format(value))
            yield from self.websocket.send(value)
            app.logger.debug("sent value back to client")


app.run("localhost", 8765, debug=True)
