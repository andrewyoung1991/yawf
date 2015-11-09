import os
import tempfile
import shutil
from unittest import mock

import pytest

from yawf import App
from yawf.commands.core import shell, run, new_command, init
from yawf.commands import call_command


def test_shell_command_without_app_set():
    command = shell.Command()
    with pytest.raises(AttributeError):
        command.run_command(argv=[])


def test_shell_command_with_mock_app():
    app = mock.MagicMock(App)()
    command = shell.Command(app=app)

    with mock.patch("yawf.commands.core.shell.Command.load_bpython") as bp:
        command.run_command(argv=["--interface", "bpython"])
        assert bp.called
        bp.assert_called_with(app=app, settings=app.settings)

    with mock.patch("yawf.commands.core.shell.Command.load_ipython") as ip:
        command.run_command(argv=["--interface", "ipython"])
        assert ip.called
        ip.assert_called_with(app=app, settings=app.settings)


def test_plain_shell_command_with_mock_app():
    app = mock.MagicMock(App)()
    command = shell.Command(app=app)

    with mock.patch("yawf.commands.core.shell.Command.load_plain") as lp:
        command.run_command(argv=["--plain"])
        assert lp.called
        lp.assert_called_with(app=app, settings=app.settings)


def test_run_server():
    app = mock.MagicMock(App)()
    command = run.Command(app=app)
    command.run_command(argv=[])
    assert app.run.called
    assert app.settings.get.called
    app.settings.get.called_with("debug", True)
    app.run.called_with("0.0.0.0", "8765", debug=True)


@mock.patch("builtins.open", create=True)
def test_new_command(m):
    reader = m().__enter__().read = mock.Mock(side_effect="$name")
    writer = m().__enter__().write = mock.Mock(side_effect="$name")
    app = mock.MagicMock(App, settings=mock.Mock(base_dir="here"))()
    command = new_command.Command(app=app)
    command.run_command(argv=["tester"])
    assert m.called
    assert reader.called
    assert writer.called


def test_init_command():
    create_path = os.path.join(tempfile.mkdtemp())
    try:
        shutil.rmtree(create_path)
    except FileNotFoundError:
        pass

    command = init.Command()
    command.run_command(argv=["tester", "--app-dir", create_path])
    app_path = os.path.join(create_path, "tester")
    assert os.path.exists(app_path)
    assert os.path.isdir(app_path)

    _glob = ["tester.py", "tests.py", "commands", "__init__.py",
                "settings.py", "tests.py", "schemas.py"]
    created = os.listdir(app_path)
    for thing in _glob:
        assert thing in created

    shutil.rmtree(create_path)


def test_init_with_call_command():
    create_path = os.path.join(tempfile.mkdtemp())
    try:
        shutil.rmtree(create_path)
    except FileNotFoundError:
        pass

    call_command(argv=["init", "tester", "--app-dir", create_path])
    app_path = os.path.join(create_path, "tester")
    assert os.path.exists(app_path)
    assert os.path.isdir(app_path)

    _glob = ["tester.py", "tests.py", "commands", "__init__.py",
                "settings.py", "tests.py", "schemas.py"]
    created = os.listdir(app_path)
    for thing in _glob:
        assert thing in created

    shutil.rmtree(create_path)


def test_init_and_new_command_with_call_command():
    create_path = os.path.join(tempfile.mkdtemp())
    try:
        shutil.rmtree(create_path)
    except FileNotFoundError:
        pass

    call_command(argv=["init", "tester", "--app-dir", create_path])
    app_dir = os.path.join(create_path, "tester")
    app_path = os.path.join(app_dir, "tester.py")

    call_command(argv=["new_command", "testit", "--app-path", app_path])
    assert os.path.exists(os.path.join(app_dir, "commands", "testit.py"))

    shutil.rmtree(create_path)
