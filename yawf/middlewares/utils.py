import functools as ft
import asyncio
import importlib

from yawf.conf import settings, make_setting


@asyncio.coroutine
@ft.lru_cache(maxsize=100)
def import_middleware(module_path):
    path, middleware = module_path.rsplit(".", 1)
    module = importlib.import_module(path)
    middleware = getattr(module, middleware, None)
    if middleware is not None:
        middleware = middleware()
    return middleware


@asyncio.coroutine
def collect_middleware():
    modules = []
    for middleware in settings.get("middleware", []):
        modules.append(import_middleware(middleware))

    if len(modules):
        modules = yield from asyncio.gather(*modules)
    return filter(lambda x: x is not None, modules)
