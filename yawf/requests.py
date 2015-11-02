import asyncio
import functools as ft

from http.client import HTTPSConnection as https, HTTPConnection as http
from urllib.parse import urlparse

__all__ = ("request", "Request")


def request(method, url, *, body=None, headers=None, loop=None):
    """
    """
    req = Request(url, loop=loop)
    future = req.request(method, body=body, headers=headers)
    return future


class Request:
    """
    """
    def __init__(self, url, *, loop=None):
        self.headers = {}
        self.body = ""
        self.url = url
        self.method = "GET"
        self.parsed = urlparse(url)
        self.loop = loop if loop is not None else asyncio.get_event_loop()

    def __str__(self):
        return "<{0} :: {1} -> {2}]".format(
            self.__class__.__name__, self.method, self.url)
    __repr__ = __str__

    def get_connection(self):
        scheme = self.parsed.scheme
        host = self.parsed.netloc
        if scheme == "http":
            return http(host)
        elif scheme == "https":
            return https(host)
        raise ValueError("no scheme provided in url.")

    def set_headers(self, **headers):
        self.headers.update(headers)
        return headers

    def pop_headers(self, *keys):
        removed = {}
        for key in keys:
            removed[key] = self.headers.pop(key, None)
        return removed

    def request(self, method, *, body=None, headers=None):
        headers = headers or {}
        self.set_headers(**headers)
        self.body = body or self.body
        self.method = method.upper()
        connection = self.get_connection()

        @asyncio.coroutine
        def runner(future):
            path = self.parsed.path
            connection.request(method, path, self.body, self.headers)
            resp = connection.getresponse()
            resp.request = self
            future.set_result(resp)
            return resp

        future = asyncio.Future(loop=self.loop)
        asyncio.ensure_future(runner(future))
        return future

    def get(self, *, body=None, headers=None):
        return self.request("GET", body=body, headers=headers)

    def put(self, *, body=None, headers=None):
        return self.request("PUT", body=body, headers=headers)

    def post(self, *, body=None, headers=None):
        return self.request("POST", body=body, headers=headers)

    def patch(self, *, body=None, headers=None):
        return self.request("PATCH", body=body, headers=headers)

    def head(self, *, body=None, headers=None):
        return self.request("HEAD", body=body, headers=headers)

    def options(self, *, body=None, headers=None):
        return self.request("OPTIONS", body=body, headers=headers)

    def delete(self, *, body=None, headers=None):
        return self.request("DELETE", body=body, headers=headers)
