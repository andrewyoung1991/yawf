import json
import asyncio

import websockets

@asyncio.coroutine
def echo():
    websocket = yield from websockets.connect("ws://localhost:8765/echo")
    message = input("what did the duck say? ")
    yield from websocket.send(json.dumps({"message": message}))
    print("> {}".format(message))

    recieved = yield from websocket.recv()
    print("< {}".format(json.loads(recieved)))

    yield from websocket.close()

asyncio.get_event_loop().run_until_complete(echo())
