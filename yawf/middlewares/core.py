from datetime import datetime

from yawf.compatibility import yayson


class JSONMiddleware:
    """
    - load all recieved messages as json
    - dump all sent messages as json
    """

    def on_send(self, message):
        message = yayson.dumps(message)
        return message

    def on_recv(self, message):
        message = yayson.loads(message)
        return message
