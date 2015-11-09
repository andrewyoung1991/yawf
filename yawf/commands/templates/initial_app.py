import asyncio

from yawf import App

from ${name}.schemas import Hello


app = App(name="${name}")


@app.route("/")
@asyncio.coroutine
def hello_handler(ws, **kwargs):
    message = Hello(message="hello, world!")
    while ws.open:
        yield from ws.send(Hello.dumps(message))
        yield from asyncio.sleep(1)
