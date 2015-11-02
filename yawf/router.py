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
    path_desc_syntax = re.compile(
        r"(?:/[a-z]?)(?:[/a-z0-9_-]+|\{[a-z0-9_]+\})*/?"
        )
    path_group_syntax = re.compile(
        r"\{([a-z0-9_]+)\}"
        )
    route_syntax = re.compile(
        r"(?:\^/)(?:[a-z]?)(?:[/a-z0-9_-]+|\{[a-z0-9_]+\})*/?"
        )

    __slots__ = ("routes", "append_slash")

    def __init__(self, *, append_slash=False):
        self.append_slash = append_slash
        self.routes = collections.OrderedDict()

    def route(self, path_desc):
        """ wrap a handler in a route
        """
        def wrap(handler):
            if issubclass(handler, BaseHandler):
                handler = handler()
            cleaned = self.clean_path(path_desc)
            regex = self._make_regex(cleaned)
            self.routes[cleaned] = regex, handler
            return handler
        return wrap

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
        self._check(path)
        if not path.startswith("^"):
            path = "^{}".format(path)
        if not path.endswith("$"):
            needs = "$"
            if self.append_slash and not path.endswith("/"):
                needs = "/" + needs
            path = "{0}{1}".format(path, needs)
        return path

    def _check(self, path_desc):
        """ enforce the following rules:
        1) a path description may not have a name segment as its first part.
        2) a path description must start with an alphabetical character.
        3) a path description must fully match the compiled pattern rule.
        """
        if re.match(r"/\{\w+\}.*", path_desc):
            raise RouterSyntaxError("the path description {0} has a named"
                " segmant in its first position.")
        elif re.match(r"/[0-9].*", path_desc):
            raise RouterSyntaxError("the path description {0} has a number"
                " in its first position.")
        style = self.path_desc_syntax
        works = style.match(path_desc)
        if works is None or len(works.group()) != len(path_desc):
            raise RouterSyntaxError("the path description {0} did not match"
                " the route syntax style {1}".format(path_desc, style))

    def _make_regex(self, path_desc):
        """ compile the path description into a regular expression.
        """
        syntax = self.path_group_syntax
        regex = syntax.sub(
            r"(?P<\1>[a-z0-9][a-z0-9_-]*)",
            path_desc
            )
        return re.compile(regex)
