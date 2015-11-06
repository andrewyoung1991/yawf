import asyncio

from yawf import App, BaseHandler


app = App(name="test")

@app.route("/chatroom")
class Chatroom(BaseHandler):
    __slots__ = ("clients", "websocket")

    def __init__(self):
        self.websocket = None
        self.clients = set()

    @asyncio.coroutine
    def __call__(self, ws, *args, **kwargs):
        self.clients.add(ws)
        app.logger.debug(dir(ws))
        yield from self.handle(ws, *args, **kwargs)

    @asyncio.coroutine
    def handle(self, ws, *args, **kwargs):
        app.logger.debug("recieved a websocket connection")
        while ws.open:
            value = yield from ws.recv()
            if value is None:
                self.clients.remove(ws)
                break
            app.logger.debug("recieved `{}` from client".format(value))
            app.logger.debug("distributing message to {}"
                                " clients".format(len(self.clients)))
            yield from self.distribute_message(value)
        app.logger.debug("closing the websocket now.")

    @asyncio.coroutine
    def distribute_message(self, message):
        websockets = list(self.clients)
        for ws in websockets:
            if ws.open:
                app.logger.debug("sending message to {}".format(ws))
                yield from ws.send(message)
            else:
                app.logger.debug("websocket was closed, removing client")
                self.clients.remove(ws)


app.run("localhost", 8765, debug=True)
