import asyncio

from yawf import App, BaseHandler, schemas


app = App(name="test")

# Our chatroom requires two keys in our json dict
# handle -- an id for the user.
# message -- the a user would like to send.
# this schema will be used to validate both sent and recieved messages
class ChatroomSchema(schemas.MessageSchema):
    handle = schemas.StringField(validators=[
        schemas.MinLengthValidator(length=4),
        schemas.MaxLengthValidator(length=15)
        ])
    message = schemas.StringField()


@app.route("/chatroom")
class Chatroom(BaseHandler):
    recv_schema = ChatroomSchema
    send_schema = ChatroomSchema

    @asyncio.coroutine
    def handle(self, ws, *args, **kwargs):
        app.logger.debug("recieved a websocket connection")
        while ws.open:
            value = yield from self.recv_json(ws)
            if value is None:
                self.remove_websocket(ws)
                break
            app.logger.debug("recieved `{}` from client".format(value))
            app.logger.debug("distributing message to {}"
                                " clients".format(len(self.websockets)))
            yield from self.distribute_message(value)
        app.logger.debug("closing the websocket now.")

    @asyncio.coroutine
    def distribute_message(self, message):
        websockets = list(self.websockets)
        for ws in websockets:
            if ws.open:
                app.logger.debug("sending message to {}".format(ws))
                yield from self.send_json(ws, message)
            else:
                app.logger.debug("websocket was closed, removing client")
                self.remove_websocket(ws)

app.run("localhost", 8765, debug=True)
