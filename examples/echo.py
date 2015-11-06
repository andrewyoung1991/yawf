import asyncio

from yawf import App, BaseHandler


app = App(name="test")

@app.route("/echo")
class Echo(BaseHandler):
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
        app.logger.debug("closing the websocket now.")


app.run("localhost", 8765, debug=True)
