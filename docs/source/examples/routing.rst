URL ROUTING
===========

url routing in yawf is meant to be as simple as possible. here are some guidelines for creating routes.


.. code-block:: python

  import asyncio

  from yawf.router import Router


  # a router object matches incoming paths to coroutines
  r = Router()

  @r.route("/")
  @asyncio.coroutine
  def home_route(ws, **kwargs):
      pass


when an application is bootstrapped, the router object compiles all of your routes into regex. if a regex is invalid, then you will know at *compile time*. yawf routes follow a simple syntax that allows for quickly creating dynamic urls.


.. code-block:: python

  import asyncio

  from yawf.router import Router

  r = Router()
  
  @r.route("/hello/{name}/")
  @asyncio.coroutine
  def say_hello(ws, **kwargs):
      yield from ws.send("hello {}!".format(kwargs.get("name")))


in the above example you can see that a dynamic url route follows the syntax of `{ key of url part }`. this dynamic part, when matched will pass its match as a keyword argument to the coroutine function associated with it.


ROUTING IN YOUR APP
===================

while you can use the Router object directly, it is an anti pattern in yawf as the App object already wraps the pattern matching and route validation of a Router. the following example is an improvement of the prior.


.. code-block:: python

  import asyncio

  from yawf import App


  app = App(name=__name__)

  @app.route("/hello/{name}/")
  @asyncio.coroutine
  def say_hello(ws, **kwargs):
      yield from ws.send("hello {}!".format(kwargs.get("name")))


RULES IN DYNAMIC PARTS
++++++++++++++++++++++

your dynamic routes by default match the pattern `[\w_]+`. for more fine grained control over the matching of dynamic parts use the dynamic part semicolon notation -> `{<name>:<regex>}`


.. code-block:: python

  import asyncio

  from yawf import App


  app = App(name=__name__)

  # only match id's which are numberic
  @app.route("/register/{id:[0-9]+}/")
  @asyncio.coroutine
  def register_user(ws, **kwargs):
      pass
