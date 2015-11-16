import asyncio
import socket

import pytest
from websockets import serve, connect

from yawf.protocol import WebSocket


def get_next_port(host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, 0))
    _, port = sock.getsockname()
    sock.close()
    return port


@pytest.fixture
def client_server(request):
    """ returns a function that accepts parameters to start a
    client and server for handler testing purposes. it is on the
    part of the test to stop the client and server.

    .. code-block:: python

        import asyncio

        from myapp import myhandler


        def test_something(client_server):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            client, server = client_server(myhandler, loop=loop)
            loop.run_until_complete(client.send("ping"))
            response = loop.run_until_complete(client.recv())
            assert response == 'pong'

    """
    def build(handler, host="localhost", port=None, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        port = port or get_next_port(host)

        server = serve(handler, host, port, klass=WebSocket, loop=loop)
        server = loop.run_until_complete(server)

        client = connect("ws://{}:{}".format(host, port))
        client = loop.run_until_complete(client)
        return client, server

    return build
