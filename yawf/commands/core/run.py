from .. import BaseCommand


class Command(BaseCommand):
    """
    """
    description = "run the websocket server."

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            default="0.0.0.0",
            )
        parser.add_argument(
            "--port",
            default="8756"
            )

    def handle(self, options):
        debug = self.app.settings.get("debug", True)
        self.app.run(
            options.host,
            options.port,
            debug=debug
            )
