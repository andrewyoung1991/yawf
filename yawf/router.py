import asyncio
import collections
import functools as ft
import re

from .base import BaseHandler


class RouterSyntaxError(Exception):
    """ raise exception if the syntax of a route does not follow the correct
    syntax.
    """


class RouterResolutionError(Exception):
    """ raise an error if we are unable to resolve a route.
    """


class Router:
    """ a router for a websocket application
    """
    path_strip = re.compile(r"^[\^?/]+|[/\$?]+$")
    path_desc_syntax = re.compile(r"[\w_]+")
    path_group_syntax = re.compile(r"""
        \{                              # group opening character
            (?P<name>[a-zA-Z][\w_]+)    # group name
            (?::(?P<pattern>.+?))?      # optional group regex
        \}                              # group closing character
        """, re.VERBOSE)

    __slots__ = ("routes",)

    def __init__(self):
        self.routes = collections.OrderedDict()

    def __str__(self):
        return "{0}({1})".format(self.__class__.__name__, str(list(self.routes.keys())))
    __repr__ = __str__

    def route(self, path_desc):
        """ wrap a handler in a route
        """
        def wrap(handler):
            if issubclass(handler, BaseHandler):
                handler = handler.as_handler()
            regex = self._make_regex(self.clean_path(path_desc))
            self.routes[path_desc] = regex, handler
            return handler
        return wrap

    @ft.lru_cache(maxsize=100)
    def resolve(self, path):
        """ resolve the path, returning the keywords dict and its handler.
        """
        for regex, handler in self.routes.values():
            match = regex.match(path)
            if match is not None:
                return match.groupdict(), handler
        raise RouterResolutionError("could not resolve the path {0}"
            " tried {1}".format(path, list(self.routes.keys())))

    __call__ = resolve

    def clean_path(self, path):
        """ add some path components into the path description, the resulting
        desc will look like this '^/...pathstuff.../?$', the trailing slash is
        optional.
        """
        # strip starting and trailing /'s and start and end regex characters
        stripped = self.path_strip.sub("", path)
        parts = stripped.split("/")
        return parts

    def _check(self, parts):
        if self.path_group_syntax.match(parts[0]):
            raise RouterSyntaxError("the path description has a dynamic"
                " segmant in first position {}".format(parts[0]))

        for part in parts:
            match = self.path_group_syntax.match(part)
            if match is None:
                match = self.path_desc_syntax.match(part)

            if match is None:
                raise RouterSyntaxError("invalid path description.")

    def _make_regex(self, path_parts):
        """ compile the path description into a regular expression.
        """
        if len(path_parts) == 1 and not any(path_parts):
            return re.compile("^/$")

        self._check(path_parts)
        parts = []
        for part in path_parts:
            match = self.path_group_syntax.match(part)
            if match is not None:
                groups = match.groupdict()
                groups["pattern"] = groups["pattern"] or "[\w_]+"
                part = "(?P<{name}>{pattern})".format(**groups)
            parts.append(part)

        regex = "^/{}/?$".format("/".join(parts))
        return re.compile(regex)
