import os
import sys
from io import StringIO
from unittest import mock

import pytest

from yawf.commands import BaseCommand, yawf


def test_create_command():
    myprint = mock.Mock()

    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser.add_argument(
                "thing",
                help="print this thing"
                )

        def handle(self, options):
            myprint(options.thing)

    hello = Command()
    hello(thing="world")
    myprint.assert_called_with("world")
    assert hello.name == "test_commands"


def test_call_command_with_argv():
    myprint = mock.Mock()

    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser.add_argument(
                "thing",
                help="print this thing"
                )

        def handle(self, options):
            myprint(options.thing)

    hello = Command()
    hello.run_command(["world"])
    myprint.assert_called_with("world")
    assert hello.name == "test_commands"


def test_yawf_main_command_not_found():
    with pytest.raises(SystemExit) as err:
        yawf.call_command(argv=["doesnotexist"])
        assert err == "command `doesnotexist` not found."

def test_yawf_main_echo_commad():
    sys.stdout = captured = StringIO()
    yawf.call_command(argv=["echo", "testing"])
    assert captured.getvalue() == "echoing message:: testing\n"
    sys.stdout = sys.__stdout__


def test_yawf_main_no_input():
    with pytest.raises(SystemExit):
        yawf.call_command(argv=[])


def test_yawf_load_settings():
    with pytest.raises(ImportError):
        yawf.load_app_settings("/this/fake/path/modulex.py")

def test_yawf_main_with_app_path():
    with pytest.raises(ImportError):
        yawf.call_command(argv=["test", "-a", "/this/fake/path/modulex.py"])


@mock.patch("yawf.commands.yawf.load_app_settings", return_value="modulex")
def test_yawf_main_working_module(mock_load_settings):
    with pytest.raises(SystemExit) as err:
        yawf.call_command(argv=["test", "-a", "/this/fake/path/modulex.py"])
        assert err == "command `test` not found."
    assert mock_load_settings.called
    mock_load_settings.assert_called_with("/this/fake/path/modulex.py")


@mock.patch("yawf.commands.yawf.import_and_run", side_effect=[False, True])
@mock.patch("yawf.commands.yawf.load_app_settings", return_value="modulex")
def test_yawf_main_working_module(mock_load_settings, mock_run):
    yawf.call_command(argv=["test", "-a", "/this/fake/path/modulex.py"])
    assert mock_load_settings.called
    mock_load_settings.assert_called_with("/this/fake/path/modulex.py")
    assert mock_run.called
    mock_run.assert_called_with([], "modulex.commands.test")
