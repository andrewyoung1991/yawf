"""
"""
import os
import sys
import argparse
import importlib


def load_app_settings(app_path):
    """ add the application to the python path and load (initialize) its
    settings module
    """
    app_path = os.path.abspath(app_path)
    app_dir = os.path.dirname(app_path)
    module_name = app_dir.rsplit("/", 1)[-1]
    sys.path.insert(0, app_dir)
    # load settings module
    importlib.import_module("{}.settings".format(module_name))
    return module_name


def run_module_command(command_module, argv):
    """ given a command module and arguments, run the modules command.
    """
    command_obj = command_module.Command()
    command_obj.run_command(argv)


def import_and_run(commandv, module_path, anchor=None):
    """ import the module and run its command
    """
    try:
        command_module = importlib.import_module(module_path, anchor)
        if command_module is not None:
            run_module_command(command_module, commandv)
            return True
    except ImportError:
        pass


def parse_argv(argv):
    parser = argparse.ArgumentParser(
        prog="yawf",
        description="a commandline proxy to builtin and custom yawf commands.",
        usage="yawf <command> [-h] :: yawf echo 'hello, world!'",
        add_help=False
        )
    parser.add_argument("command", nargs="?", default=None)
    parser.add_argument("-a", dest="app_path", default=None,
        help="path to the python file containing your app declaration.")
    return parser


def call_command(*, argv=None):
    """ call a command with either sys.argv or a given argv list
    """
    parser = parse_argv(argv or sys.argv[1:])
    args, commandv = parser.parse_known_args(argv)
    command = args.command
    app_path = args.app_path

    if command is None:
        parser.print_help()
        sys.exit(0)

    module = None
    if app_path is not None:
        module = load_app_settings(app_path)

    # try builtin
    ran = import_and_run(commandv, "..core.{}".format(command), __name__)
    if ran:
        return

    if module is not None:
        # try custom
        module = "{0}.commands.{1}".format(module, command)
        ran = import_and_run(commandv, module)
        if ran:
            return

    sys.exit("command `{}` not found.".format(command))
