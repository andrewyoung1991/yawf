import os

from .. import BaseCommand
from ..utils import load_core_template


class Command(BaseCommand):
    """
    """
    description = ""

    def add_arguments(self, parser):
        parser.add_argument(
            "command_name",
            help="the name of the command you are implementing"
            )

    def handle(self, options):
        commands_dir = os.path.join(self.app.settings.base_dir, "commands")
        command_file = options.command_name + ".py"

        with open(os.path.join(commands_dir, command_file), "w") as cmnd:
            template = load_core_template("blank_command.py")
            context = {"command_name": options.command_name}
            cmnd.write(template.safe_substitute(context))
