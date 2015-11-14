import sys
import functools as ft
from glob import iglob

try:
    import ujson as json
except ImportError:  # pragma: no cover
    import json as json

try:
    from asyncio import ensure_future
except ImportError:  # pragma: no cover
    from asyncio import async as ensure_future


__all__ = ("yayson", "ensure_future", "PY35", "iglob")


PY35 = sys.version_info.minor > 4

if PY35:
    iglob = ft.partial(iglob, recursive=True)

yayson = json

def _default(obj):  # pragma: no cover
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

yayson.dumps = ft.partial(yayson.dumps, default=_default)

ensure_future = ensure_future
