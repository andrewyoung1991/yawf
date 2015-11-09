import os
import sys
import argparse
import importlib

from .base import BaseCommand
from .utils import find_commands
from .core import *  # noqa
from .colors import color_msg

__all__ = ("BaseCommand", "call_command")


def load_app_settings(app_path):
    """ add the application to the python path and load (initialize) its
    settings module
    """
    app_path, _ = os.path.splitext(os.path.abspath(app_path))
    app_dir = os.path.dirname(app_path)
    app_module = ".".join(app_path.rsplit("/", 2)[-2:])
    module_name = app_dir.rsplit("/", 1)[-1]
    sys.path.insert(0, os.path.dirname(app_dir))
    # load settings module
    app = importlib.import_module(app_module)
    importlib.import_module("{}.settings".format(module_name))
    return module_name, app.app


def run_module_command(command_module, argv, app=None):
    """ given a command module and arguments, run the modules command.
    """
    command_obj = command_module.Command(app=app)
    command_obj.run_command(argv)


def import_and_run(commandv, module_path, app=None):
    """ import the module and run its command
    """
    try:
        command_module = importlib.import_module(module_path)
        if command_module is not None:
            run_module_command(command_module, commandv, app)
            return True
    except ImportError:
        pass


def parse_argv(argv):
    parser = argparse.ArgumentParser(
        prog=color_msg("bold", color_msg("underline", "yawf")),
        description=color_msg("okgreen", "a commandline interface"
                                " to builtin and custom yawf commands."),
        usage=color_msg("okblue", "yawf [--list] [<command> [-h]] ::"
                        " yawf echo 'hello, world!'"),
        add_help=False
        )
    parser.add_argument("command", nargs="?", default=None,
        help="the name of the builtin or custom command you'd like to run.")
    parser.add_argument("--list", dest="list_commands", action="store_true",
        default=False, help="list available commands")
    parser.add_argument("--app-path", dest="app_path", default=None,
        help="path to the python file containing your app declaration.")
    return parser


def list_commands(app_path):  # pragma: no cover
    app_commands = None
    if app_path is not None:
        app_commands_dir = os.path.join(os.path.dirname(app_path), "commands")
        app_commands = find_commands(app_commands_dir)
        app_commands = "{}".format("\n".join(app_commands))

    core_dir = os.path.join(os.path.dirname(__file__), "core")
    builtin_commands = find_commands(core_dir)
    builtin_commands = "{}".format("\n".join(builtin_commands))

    print(color_msg("bold", "\n:: available commands ::\n"))
    print(color_msg("header", "[ core ]"))
    print(color_msg("okblue", builtin_commands))
    if app_commands is not None:
        print(color_msg("header", "[ app ]"))
        print(color_msg("okblue", app_commands))


def call_command(*, argv=None):
    """ call a command with either sys.argv or a given argv list
    """
    parser = parse_argv(argv or sys.argv[1:])
    args, commandv = parser.parse_known_args(argv)

    command = args.command
    app_path = args.app_path or os.getenv("YAWF_APP_PATH", None)

    if args.list_commands:  # pragma: no cover
        parser.print_help()
        list_commands(app_path)
        sys.exit(0)

    if command is None:  # pragma: no cover
        parser.print_help()
        sys.exit(0)

    module = None
    app = None
    if app_path is not None:
        module, app = load_app_settings(app_path)

    # try builtin
    core_module = "yawf.commands.core.{}".format(command)
    ran = import_and_run(commandv, core_module, app)
    if ran:
        return

    if module is not None:
        # try custom
        module = "{0}.commands.{1}".format(module, command)
        ran = import_and_run(commandv, module, app)
        if ran:
            return

    sys.exit("command `{}` not found.".format(command))
