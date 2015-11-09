from yawf.commands.base import BaseCommand


class Command(BaseCommand):
    """ ${command_name}
    """
    description = ""

    def add_arguments(self, parser):
        pass

    def handle(self, options):
        pass
