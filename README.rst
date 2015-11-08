====
YAWF
====
------------------------------
yeah, a websocket framework...
------------------------------


.. image:: https://travis-ci.org/andrewyoung1991/yawf.svg?branch=master
    :target: https://travis-ci.org/andrewyoung1991/yawf


.. image:: https://coveralls.io/repos/andrewyoung1991/yawf/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/andrewyoung1991/yawf?branch=master

.. image:: https://api.codacy.com/project/badge/grade/821539edd9244e32b1a5e899c6a1f639
    :target: https://www.codacy.com/app/andrewyoung1991/yawf


YAWF is a reaction to a few modern python web frameworks reactions to websockets. While trying to implement a decent websocket server is tricky, huge advances in async python (i.e. asyncio) are begining to alleviate the pains. No longer will you have to import a coroutine library monkey patch all the things.

==========
Quickstart
==========

YAWF attempts to be the Flask of websocket application servers, which is cool becuase, well, the web needs websockets now, and the web needs python, and python web developers know how to hook things up with Flask pretty quickly, so that means YAWF should be pretty great.

.. code-block:: python

    # /app.py
    import asyncio

    from yawf import App


    ws_app = App(name="my app")

    @ws_app.route("/echo")
    @asyncio.coroutine
    def echo_handler(ws, **kwargs):
        # whatever i recieve from this socket i'll send right back
        while True:
            message = yield from ws.recv()
            yield from ws.send(message)

    if __name__ == "__main__":
        ws_app.run()

.. code-block:: bash

    $ python app.py


to configure your project just import the global Settings object:

.. code-block:: python

    # /settings.py
    from yawf import Settings

    s = Settings()
    s.secret = "i love the 80's was a good show"

    # /app.py
    from yawf.conf import settings

    assert settings.secret == "i love the 80's was a good show"

but don't you dare try to change your settings a runtime!

.. code-block:: python

    # /app.py
    from yawf.conf import settings

    settings.secret = "i changed my mind, i prefer i love the 70's"
    ---------------------------------------------------------------
    Exception
    ...
    ----> settings.secret = "i changed my mind, i prefer i love the 70's"

    FrozenObjectError: cannot set attributes of a frozen object


    # but if you really really need to change something at runtime
    from yawf.conf import make_setting

    make_setting("secret", "okay i guess i love the 80's is cooler")
  
=========
Structure
=========

YAWF is built with the microservice architecture in mind, because perhaps you are like me and you'd rather not mess around with hacking Django or Flask to catch websocket requests before they taint your WSGI server, and you think it might be cool to give a single machine full power to connect your clients websockets.
