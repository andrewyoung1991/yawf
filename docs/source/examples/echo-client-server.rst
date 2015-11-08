Echo Client & Server
====================

to begin we will start initialize a YAWF App named `echo test`

.. code-block:: python

    # app.py

    import yawf

    app = yawf.App(name="echo test")

Server
++++++

When handling a websocket requests, there are two types of handlers which can be used. The quickest and easiest is just a coroutine which excepts a websocket connection and kwargs from matches in its url pattern.

.. code-block:: python

    # app.py

    import asyncio
    import yawf

    app = yawf.App(name="echo test")

    @app.route("/echo")
    @asyncio.coroutine
    def echo_handler(websocket, **kwargs):
        pass

The handler above will be bound to the websocket endpoint `/echo`. When this endpoint is called by a client a websocket object will be passed into the coroutine, allowing our echo handler to communicate directly with its client. In this example no kwargs will be passed into the handler, because the route `/echo` does not include any named patterns to match, but it is important that a handler must always accept kwargs. Lets add the echo functionality:

.. code-block:: python

    # app.py

    import asyncio
    import yawf

    app = yawf.App(name="echo test")

    @app.route("/echo")
    @asyncio.coroutine
    def echo_handler(websocket, **kwargs):
        while websocket.open:
            message = yield from websocket.recv()
            if message is None:
                break
            yield from websocket.send(message)

The `echo_handler` will wait for any message from a client and as long as the message is not `None` it will return the message directly back to the websocket connection, cool right? It's kind of boring, but this is actually the entry point to websocket programming, demonstrating the ping-pong loop. In `echo_handler` we recieve a ping from some client and return a pong (the same message sent back as soon as possible). This loop is incredibly useful for monitoring connections with clients. For example in a realtime application where user activity must be monitored, i.e. your backend needs to know who is online at any given time, you might consider using a ping-pong loop over the old fashioned measurement tools such as capturing the last time a user made a request.

It is important to note here that it is currently best practice in YAWF to check the validity of a message from a client before performing any further actions. At the very least, a handler should confirm that a websocket is open and that a recieved message is not None (indicating the websocket is closing or closed before the `websocket.recv` coroutine was resolved).

Lets build out this handler to actually do something usefull, to monitor a users connection status and store it in a redis database.

.. code-block:: python

    # app.py

    import asyncio

    import redis

    from yawf import App, schemas, auth


    app = yawf.App(name="echo test")
    token_auth = auth.JWTTokenAuth()
    db = redis.StrictRedis()


    class EchoSchema(schemas.MessageSchema):
        jwt = schemas.StringField()


    @app.route("/echo")
    @asyncio.coroutine
    def echo_handler(websocket, **kwargs):
        user_id = None

        while websocket.open:
            message = yield from websocket.recv()
            if message is None:
                break

            # validate the message schema, and parse its contents.
            try:
                parsed = EchoSchema.loads(message)
            except AssertionError:
                yield from websocket.close(code=1007, reason="Invalid Message")
                break

            # validate the JWT and parse it.
            token = token_auth.validate(parsed.jwt)
            if token is not None:
                user_id = token["id"]
                db.hset(user_id, "connected", True)
                yield from websocket.send(message)
            else:
                yield from websocket.close(code=1007, reason="Expired Token")
                break

        # when the ping pong loop breaks we can mark the user as no longer connected
        if user_id is not None:
            db.hset(user_id, "connected", False)

The above `echo_handler` is now a decent amount more usefull, and other services of your web application
can consume the user data from your redis db.

Client
++++++

lets build out a simple javascript client to communicate with our ping-pong loop.

.. code-block:: javascript
    
    // pingPongClient.js

    (function() {
      var ws = new WebSocket("ws://localhost:8765/echo");

      ws.onopen = function(event) {
        console.log("websocket connection is open!");
        sendPing();
      };

      ws.onmessage = function(event) {
        console.log("recieved a pong from the server", event.data);
        sendPing();
      };

      function sendPing() {
        var message = {};
        // retrieve the JWT you fetched from the api or whatever.
        message.jwt = window.localStorage.JWT;
        ws.send(JSON.stringify(message));
      }
    })();
