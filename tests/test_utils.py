import pytest

from yawf import utils
from yawf.conf import patch_settings, settings


def test_frozen_objects_raise_errors():
    f = utils.Frozen(None)
    with pytest.raises(utils.Frozen.FrozenObjectError) as err:
        f.hello = 1
        assert err == "cannot set attributes of a frozen object"


def test_patch_settings_raises_errors_and_resets():
    cached_this = settings.get("this")

    @patch_settings(this="that")
    def ultimate_test():
        assert settings.this == "that"
        raise ValueError("shreeeed")

    with pytest.raises(ValueError) as err:
        ultimate_test()
        assert err == "shreeeed"
        assert settings.get("this") == cached_this


def test_lazy_property():

    class tester:
        @utils.lazyprop
        def say_hi(self):
            return "hi"

    testit = tester()
    assert hasattr(testit, "_lazy_say_hi") is False
    assert testit.say_hi == "hi"
    assert testit._lazy_say_hi == "hi"
