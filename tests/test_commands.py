import os
import sys
from io import StringIO
from collections import namedtuple
from unittest import mock

import pytest

from yawf.commands import BaseCommand, call_command, load_app_settings
from yawf.commands import utils


def test_loading_core_templates():
    template = utils.load_core_template("initial_app.py")
    assert template.template is not None


def test_loading_unknown_template():
    with pytest.raises(FileNotFoundError) as err:
        utils.load_core_template("t#ia#l_app.py")
        assert err == "t#ia#l_app.py checked {}".format(utils.TEMPLATE_DIR)


def test_create_command():
    myprint = mock.Mock()
    Options = namedtuple("Options", ["thing"])

    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser.add_argument(
                "thing",
                help="print this thing"
                )

        def handle(self, options):
            myprint(options.thing)

    hello = Command()
    hello.handle(Options(thing="world"))
    myprint.assert_called_with("world")
    assert hello.name == "test_commands"


def test_call_command_with_argv():
    myprint = mock.Mock()
    Options = namedtuple("Options", ["thing"])

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
        call_command(argv=["doesnotexist"])
        assert err == "command `doesnotexist` not found."


def test_yawf_main_no_input():
    with pytest.raises(SystemExit):
        call_command(argv=[])


def test_yawf_load_settings():
    with pytest.raises(ImportError):
        load_app_settings("/this/fake/path/modulex.py")

def test_yawf_main_with_app_path():
    with pytest.raises(ImportError):
        call_command(argv=["test", "--app-path", "/this/fake/path/modulex.py"])


@mock.patch("yawf.commands.load_app_settings", return_value=("modulex", None))
def test_yawf_main_working_module(mock_load_settings):
    with pytest.raises(SystemExit) as err:
        call_command(argv=["test", "--app-path", "/this/fake/path/modulex.py"])
        assert err == "command `test` not found."
    assert mock_load_settings.called
    mock_load_settings.assert_called_with("/this/fake/path/modulex.py")


@mock.patch("yawf.commands.import_and_run", side_effect=[False, True])
@mock.patch("yawf.commands.load_app_settings", return_value=("modulex", None))
def test_yawf_main_working_module_fake(mock_load_settings, mock_run):
    call_command(argv=["test", "--app-path", "/this/fake/path/modulex.py"])
    assert mock_load_settings.called
    mock_load_settings.assert_called_with("/this/fake/path/modulex.py")
    assert mock_run.called
    mock_run.assert_called_with([], "modulex.commands.test", None)
