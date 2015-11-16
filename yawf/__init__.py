import abc
import asyncio
from datetime import datetime
import importlib
import logging
from urllib.parse import urlparse, parse_qs

from websockets import serve

from .router import Router, RouterResolutionError
from .base import BaseHandler
from .conf import Settings, settings
from .utils import singleton
from .middlewares.utils import collect_middleware
from .protocol import WebSocket


__all__ = ("App", "Router", "BaseHandler", "settings", "Settings")
__version__ = "0.0.1"


@singleton()
class App:
    """ App is a singleton class, meaning one app per application... duh!
    """
    def __init__(self, *, name=None, debug=False):
        self.name = name
        self.router = Router()
        self.logger = logging.getLogger(self.name)
        self.settings = settings
        self._debug = debug

    def __str__(self):
        return "<{0} :: {1}>".format(self.__class__.__name__, self.name)
    __repr__ = __str__

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        if value is True:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self._debug = value
        return self._debug

    def route(self, path):
        """
        proxy to the router allowing for the syntax:
        ::

            app = App()

            @app.route("/")
            @asyncio.coroutine
            def handler(ws, **kwargs):
                pass
        """
        return self.router.route(path)

    def as_handler(self, *, loop=None, debug=False):
        """ return the router as a coroutine resolving paths as they are
        requested.

        ::
            import asyncio

            from websockets import server

            from yawfn import App

            app = App()

            @app.route('/echo/')
            async def echo(ws, *args, **kwargs):
                value = await ws.recv()
                await ws.send(value)

            loop = asyncio.get_event_loop
            ws_server = server.serve(app.as_handler(), "localhost", 8765)
            loop.run_until_complete(ws_server)
            loop.close()
        """
        loop = loop if loop is not None else asyncio.get_event_loop()

        @asyncio.coroutine
        def router(ws, path):
            _msg = "{0} -> is open? -> {1}".format(ws, ws.open)
            path = urlparse(path)
            self.logger.debug(_msg)
            try:
                kwargs, handler = self.router.resolve(path.path)
            except RouterResolutionError as err:
                _msg = "{0} -> {1}".format(ws, err)
                self.logger.debug(_msg)
                yield from ws.close(code=1011, reason="{}".format(err))
                return

            _msg = "{0} -> resolved path -> {1}".format(path, handler)
            self.logger.debug(_msg)

            _msg = "{} -> launching handler".format(ws)
            self.logger.debug(_msg)
            kwargs["LOOP"] = loop
            kwargs["QUERY"] = parse_qs(path.query)
            yield from handler(ws, **kwargs)
            yield from ws.close()
            _msg = "{} -> closed".format(ws)
            self.logger.debug(_msg)

        return router

    @staticmethod
    @asyncio.coroutine
    def run_middlewares(message, *, on="recv"):
        middlewares = yield from collect_middleware()
        routines = []
        for middleware in middlewares:
            handler = middleware.delegate(on=on)
            if handler is not None:
                routines.append(handler)
        if on == "send":
            routines = reversed(routines)

        for routine in routines:
            message = yield from routine(message)
            assert message is not None, "A middleware returned an invalid message"

        return message

    def run(self, host, port, *, debug=False, loop=None):
        self.debug = debug
        loop = loop if loop else asyncio.get_event_loop()
        server = serve(self.as_handler(loop=loop), host, port, klass=WebSocket)

        try:
            print("Websocket server started -> {0}:{1}\n"
                "Press <Ctrl-c> to stop...".format(host, port))
            loop.run_until_complete(server)
            loop.run_forever()
        except KeyboardInterrupt:  # pragma: no cover
            print("Shutting down the server...")
        finally:
            server.close()
            loop.close()
            print("OKAY BYE!")
