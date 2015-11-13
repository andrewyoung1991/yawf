import asyncio

import pytest

from yawf.middlewares import Middleware
from yawf.middlewares import utils, core
from yawf.conf import patch_settings


def test_invalid_middleware():
    with pytest.raises(TypeError) as err:
        Middleware()
        assert err == "Middleware must implement either `on_recv` or `on_send`"


def test_middleware_delegate():
    class m(Middleware):
        def on_send(self, message):
            return message

    middleware = m()
    assert m._isvalid
    assert callable(middleware.delegate(on="on_send"))
    assert middleware.delegate(on="on_recv") is None


@patch_settings(middleware=["yawf.middlewares.core.JSONMiddleware"])
def test_middleware_loading():
    @asyncio.coroutine
    def testit():
        module, *_ = yield from utils.collect_middleware()
        assert isinstance(module, core.JSONMiddleware)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(testit())
