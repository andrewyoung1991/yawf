import asyncio
from unittest import mock

import pytest

from yawf import App, BaseHandler
from yawf.router import RouterResolutionError


@pytest.fixture
def evloop():
    return asyncio.get_event_loop()

@pytest.fixture
def mock_socket():
    @asyncio.coroutine
    def recv():
        return "hello"

    @asyncio.coroutine
    def send(msg):
        return msg

    @asyncio.coroutine
    def close(*args, **kwargs):
        return

    mock_socket = mock.Mock(
        recv=mock.Mock(wraps=recv),
        send=mock.Mock(wraps=send),
        close=mock.Mock(wraps=close)
        )
    return mock_socket

@pytest.fixture
def mock_loop():
    @asyncio.coroutine
    def run_until_complete(server):
        return server

    @asyncio.coroutine
    def run_forever():
        yield from asyncio.sleep(0.1)

    @asyncio.coroutine
    def close(*args, **kwargs):
        return

    mock_loop = mock.Mock(
        run_until_complete=mock.Mock(wraps=run_until_complete),
        run_forever=mock.Mock(wraps=run_forever),
        close=mock.Mock(wraps=close)
        )
    return mock_loop


def test_application(evloop, mock_socket):
    app = App(name="testapp")

    @app.route("/")
    class Echo(BaseHandler):
        @asyncio.coroutine
        def handle(self, ws, **kwargs):
            from_client = yield from ws.recv()
            yield from ws.send(from_client)

    _, handler = app.router.resolve("/")

    @asyncio.coroutine
    def run_handler():
        yield from handler(mock_socket)
        assert mock_socket.recv.called
        assert mock_socket.send.called
        mock_socket.send.assert_called_with("hello")

    evloop.run_until_complete(run_handler())


def test_application_as_handler(evloop, mock_socket):
    app = App(name="testapp")

    @app.route("/")
    class Echo(BaseHandler):
        @asyncio.coroutine
        def handle(self, ws, **kwargs):
            from_client = yield from ws.recv()
            yield from ws.send(from_client)

    handler = app.as_handler(loop=evloop)

    @asyncio.coroutine
    def run_handler():
        yield from handler(mock_socket, "/")
        assert mock_socket.recv.called
        assert mock_socket.send.called
        mock_socket.send.assert_called_with("hello")

    evloop.run_until_complete(run_handler())


def test_application_as_handler_unknown_route(evloop, mock_socket):
    app = App(name="testapp")

    @app.route("/")
    class Echo(BaseHandler):
        @asyncio.coroutine
        def handle(self, ws, **kwargs):
            from_client = yield from ws.recv()
            yield from ws.send(from_client)

    handler = app.as_handler(loop=evloop)

    @asyncio.coroutine
    def run_handler():
        yield from handler(mock_socket, "/echo")
        assert mock_socket.close.called
        error = "could not resolve the path /echo tried "\
                "{}".format(list(app.router.routes.keys()))
        mock_socket.close.assert_called_with(code=1011, reason=error)

    evloop.run_until_complete(run_handler())


def test_run_app(evloop, mock_loop):
    app = App(name="testapp")
    app.run("localhost", 8765, loop=mock_loop)
    assert mock_loop.run_until_complete.called
    assert mock_loop.run_forever.called
    assert mock_loop.close.called


def test_run_app_debug(evloop, mock_loop):
    app = App(name="testapp")
    app.run("localhost", 8765, debug=True, loop=mock_loop)
    assert app.logger.level == 10  # debug
    assert app.debug is True
