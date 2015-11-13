import asyncio
import importlib

from yawf.conf import settings, make_setting


@asyncio.coroutine
def import_middleware(module_path):
    path, middleware = module_path.rsplit(".", 1)
    module = importlib.import_module(path)
    middleware = getattr(module, middleware, None)
    if middleware is not None:
        middleware = middleware()
    return middleware


@asyncio.coroutine
def collect_middleware():
    if settings.get("_middleware") is None:
        modules = []
        for middleware in settings.middleware:
            modules.append(import_middleware(middleware))

        if len(modules):
            modules = yield from asyncio.gather(*modules)
        make_setting("_middleware", modules)
    return settings._middleware
