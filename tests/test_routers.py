import pytest

from yawf import router

def test_router_appends_slash():
    urls = router.Router()
    urls.route("/this")(lambda x: x)
    regex, _ = urls.routes["/this"]
    assert regex.pattern.endswith("/?$")

@pytest.mark.parametrize("route, path, expect", [
    ("/this/{that}", "/this/1", {"that": "1"}),
    ("/api/{obj}/{pk}/", "/api/racoons/99/", {"obj": "racoons", "pk": "99"}),
    ("/api/{obj}/{pk}/detail/", "/api/racoons/99/detail/", {"obj": "racoons", "pk": "99"}),
    ])
def test_router_matches_regex(route, path, expect):
    urls = router.Router()
    urls.route(route)(lambda x: x)
    regex, _ = urls.routes[route]
    keywords = regex.match(path).groupdict()
    assert keywords is not None
    assert 0 < len(keywords)
    assert keywords == expect

@pytest.mark.parametrize("route, error", [
    ("/{this}/this/", router.RouterSyntaxError),
    ("/thisis/{/", router.RouterSyntaxError),
    ])
def test_bad_routes(route, error):
    urls = router.Router()
    with pytest.raises(error):
        urls.route(route)(lambda x: x)


def test_router_resolver_returns_correct_function():
    urls = router.Router()

    @urls.route("/")
    def myhandler(request, **kwargs):
        pass

    _, handler = urls.resolve("/")
    assert handler.__name__ == myhandler.__name__


def test_unresolved_route():
    urls = router.Router()
    with pytest.raises(router.RouterResolutionError):
        urls.resolve("/")
