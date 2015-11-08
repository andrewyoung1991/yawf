from ..base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "thing",
            help="the thing to echo back"
            )

    def handle(self, options):
        print("echoing message::", options.thing)
