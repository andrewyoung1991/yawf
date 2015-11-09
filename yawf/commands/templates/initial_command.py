from yawf.commands.base import BaseCommand


class Command(BaseCommand):
    """ a somewhat un-usefull command in terms of functionality, but a good
    entry point to writing these commands.
    """
    description = "echo a message back to the clients terminal."

    def add_arguments(self, parser):
        parser.add_argument(
            "thing",
            help="the thing to echo back"
            )

    def handle(self, options):
        self.console_log("echoing message::", options.thing)
