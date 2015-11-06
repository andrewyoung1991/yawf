import asyncio

import pytest

from yawf import BaseHandler


@pytest.fixture
def evloop():
    return asyncio.get_event_loop()


def test_basehandler_without_handle(evloop):
    handler = BaseHandler()

    @asyncio.coroutine
    def run_handler():
        yield from handler(None)

    with pytest.raises(NotImplementedError):
        evloop.run_until_complete(run_handler())


def test_stupid_handler(evloop):

    class Nothing(BaseHandler):
        @asyncio.coroutine
        def handle(self, ws, *args, **kwargs):
            assert ws in self.websockets
            yield from asyncio.sleep(0.1)

    handler = Nothing()

    @asyncio.coroutine
    def run_handler():
        yield from handler("cool")

    evloop.run_until_complete(run_handler())
