import asyncio
from unittest import mock

import pytest

from yawf import App, BaseHandler
from yawf.router import RouterResolutionError


@pytest.fixture
def evloop():
    return asyncio.get_event_loop()

def test_application(evloop):
    app = App(name="testapp")

    @app.route("/")
    class Echo(BaseHandler):
        @asyncio.coroutine
        def handle(self, ws, *args, **kwargs):
            from_client = yield from ws.recv()
            yield from ws.send(from_client)

    _, handler = app.router.resolve("/")

    @asyncio.coroutine
    def run_handler():

        @asyncio.coroutine
        def recv():
            return "hello"

        @asyncio.coroutine
        def send(msg):
            return msg

        mock_socket = mock.Mock(
            recv=mock.Mock(wraps=recv),
            send=mock.Mock(wraps=send)
            )
        yield from handler(mock_socket)
        assert mock_socket.recv.called
        assert mock_socket.send.called
        mock_socket.send.assert_called_with("hello")

    evloop.run_until_complete(run_handler())


def test_application_as_handler(evloop):
    app = App(name="testapp")

    @app.route("/")
    class Echo(BaseHandler):
        @asyncio.coroutine
        def handle(self, ws, *args, **kwargs):
            from_client = yield from ws.recv()
            yield from ws.send(from_client)

    handler = app.as_handler(loop=evloop)

    @asyncio.coroutine
    def run_handler():

        @asyncio.coroutine
        def recv():
            return "hello"

        @asyncio.coroutine
        def send(msg):
            return msg

        @asyncio.coroutine
        def close():
            return

        mock_socket = mock.Mock(
            recv=mock.Mock(wraps=recv),
            send=mock.Mock(wraps=send),
            close=mock.Mock(wraps=close)
            )
        yield from handler(mock_socket, "/")
        assert mock_socket.recv.called
        assert mock_socket.send.called
        mock_socket.send.assert_called_with("hello")

    evloop.run_until_complete(run_handler())


def test_application_as_handler_unknown_route(evloop):
    app = App(name="testapp")

    @app.route("/")
    class Echo(BaseHandler):
        @asyncio.coroutine
        def handle(self, ws, *args, **kwargs):
            from_client = yield from ws.recv()
            yield from ws.send(from_client)

    handler = app.as_handler(loop=evloop)

    @asyncio.coroutine
    def run_handler():

        @asyncio.coroutine
        def recv():
            return "hello"

        @asyncio.coroutine
        def send(msg):
            return msg

        @asyncio.coroutine
        def close():
            return

        mock_socket = mock.Mock(
            recv=mock.Mock(wraps=recv),
            send=mock.Mock(wraps=send),
            close=mock.Mock(wraps=close)
            )

        yield from handler(mock_socket, "/echo")
        assert mock_socket.send.called
        assert mock_socket.close.called
        error = "could not resolve the path /echo tried "\
                "{}".format(list(app.router.routes.keys()))
        mock_socket.send.assert_called_with(error)

    evloop.run_until_complete(run_handler())


def test_run_app(evloop):
    app = App(name="testapp")

    @asyncio.coroutine
    def run_until_complete(server):
        return server

    @asyncio.coroutine
    def run_forever():
        yield from asyncio.sleep(0.1)

    @asyncio.coroutine
    def close():
        return

    mock_loop = mock.Mock(
        run_until_complete=mock.Mock(wraps=run_until_complete),
        run_forever=mock.Mock(wraps=run_forever),
        close=mock.Mock(wraps=close)
        )

    app.run("localhost", 8765, loop=mock_loop)
    assert mock_loop.run_until_complete.called
    assert mock_loop.run_forever.called
    assert mock_loop.close.called


def test_run_app_debug(evloop):
    app = App(name="testapp")

    @asyncio.coroutine
    def run_until_complete(server):
        return server

    @asyncio.coroutine
    def run_forever():
        yield from asyncio.sleep(0.1)

    @asyncio.coroutine
    def close():
        return

    mock_loop = mock.Mock(
        run_until_complete=mock.Mock(wraps=run_until_complete),
        run_forever=mock.Mock(wraps=run_forever),
        close=mock.Mock(wraps=close)
        )

    app.run("localhost", 8765, debug=True, loop=mock_loop)
    assert app.logger.level == 10  # debug
