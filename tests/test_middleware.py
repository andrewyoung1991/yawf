import asyncio

import pytest

from websockets import serve, connect

from yawf.protocol import WebSocket
from yawf.middlewares import Middleware
from yawf.middlewares import utils, core
from yawf.conf import patch_settings
from yawf.auth import JWTTokenAuth
from yawf.compatibility import yayson
from yawf import App


def test_invalid_middleware():
    with pytest.raises(TypeError) as err:
        Middleware()
        assert err == "Middleware must implement either `on_recv` or `on_send`"


def test_middleware_delegate():
    class m(Middleware):
        @asyncio.coroutine
        def on_send(self, message):
            return message

    middleware = m()
    assert m._isvalid
    assert callable(middleware.delegate(on="send"))
    assert middleware.delegate(on="recv") is None


@patch_settings(middleware=["yawf.middlewares.core.JSONMiddleware"])
def test_middleware_loading():
    @asyncio.coroutine
    def testit():
        module, *_ = yield from utils.collect_middleware()
        assert isinstance(module, core.JSONMiddleware)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(testit())


@patch_settings(middleware=["yawf.middlewares.core.JSONMiddleware"])
def test_run_middleware():
    run = App().run_middlewares
    message = '{"foo": "bar"}'

    @asyncio.coroutine
    def testit(message):
        message = yield from run(message)
        assert message == {"foo": "bar"}
        message = yield from run({"foo": "bar"}, on="send")
        assert message == '{"foo": "bar"}'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(testit(message))


@patch_settings(middleware=["yawf.middlewares.core.JSONMiddleware"])
def test_run_middleware_protocol_builder(client_server):

    @asyncio.coroutine
    def handler(ws, path):
        recvd = yield from ws.recv()
        assert recvd == {"foo": "bar"}
        yield from ws.send(recvd)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client, server = client_server(handler, loop=loop)

    loop.run_until_complete(client.send('{"foo": "bar"}'))
    reply = loop.run_until_complete(client.recv())
    assert reply == '{"foo": "bar"}'

    loop.run_until_complete(client.worker)
    server.close()
    loop.run_until_complete(server.wait_closed())


@patch_settings(secret_key="okayoky", middleware=[
    "yawf.middlewares.core.JSONMiddleware",
    "yawf.middlewares.core.JWTMiddleware"
    ])
def test_jwt_middleware(client_server):
    auth = JWTTokenAuth()
    token = auth.create(id=1, username="megaman")

    @asyncio.coroutine
    def handler(ws, path):
        recvd = yield from ws.recv()
        assert recvd["auth_user"] is not None
        assert recvd["auth_user"]["id"] == 1
        assert recvd["auth_user"]["username"] == "megaman"
        yield from ws.send(recvd)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client, server = client_server(handler, loop=loop)

    message = yayson.dumps({"foo": "bar", "authentication": token})

    loop.run_until_complete(client.send(message))
    reply = loop.run_until_complete(client.recv())
    assert reply == '{"foo": "bar"}'

    loop.run_until_complete(client.worker)
    server.close()
    loop.run_until_complete(server.wait_closed())
