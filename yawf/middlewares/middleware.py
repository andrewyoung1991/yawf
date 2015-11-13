class Middleware:
    """
    .. code-block:: python

    class MyMiddleware(Middleware):
        @asyncio.coroutine
        def on_recv(self, message):
            return message

        @asyncio.coroutine
        def on_send(self, message):
            return message
    """
    def __init__(self, websocket=None):
        self.websocket = websocket
        if not self._isvalid:
            raise TypeError("Middleware must implement either "
                "`on_recv` or `on_send`")

    @property
    def _isvalid(self):
        return hasattr(self, "on_recv") or hasattr(self, "on_send")

    def delegate(self, *, on):
        return getattr(self, on, None)
