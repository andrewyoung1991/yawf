import os

from .. import BaseCommand
from ..utils import load_core_template, generate_secret

class Command(BaseCommand):
    """
    """
    description = "create a new templated YAWF project"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_name",
            help="the name of the app you would like to create."
            )
        parser.add_argument(
            "--app-dir",
            dest="app_dir",
            nargs="?",
            default=os.path.abspath(os.path.curdir),
            help="path to the directory you would like to start the app in."
            )

    def handle(self, options):
        app_name = options.app_name
        app_dir = os.path.join(options.app_dir, app_name)
        commands_dir = os.path.join(app_dir, "commands")

        if not os.path.exists(app_dir):
            os.makedirs(app_dir)

        if not os.path.exists(commands_dir):
            os.makedirs(commands_dir)

        self.touch(os.path.join(commands_dir, "__init__.py"))
        self.touch(os.path.join(app_dir, "__init__.py"))
        self.touch(os.path.join(app_dir, "tests.py"))

        with open(os.path.join(app_dir, app_name + ".py"), "w") as app_file:
            template = load_core_template("initial_app.py")
            context = {"name": app_name}
            app_file.write(template.safe_substitute(context))

        with open(os.path.join(app_dir, "settings.py"), "w") as settings_file:
            template = load_core_template("initial_settings.py")
            context = {"secret": generate_secret()}
            settings_file.write(template.safe_substitute(context))

        with open(os.path.join(app_dir, "schemas.py"), "w") as schema_file:
            template = load_core_template("initial_schema.py")
            schema_file.write(template.safe_substitute())

        with open(os.path.join(commands_dir, "echo.py"), "w") as command_file:
            template = load_core_template("initial_command.py")
            command_file.write(template.safe_substitute())

    @staticmethod
    def touch(path):
        with open(path, "a"):
            os.utime(path, None)
