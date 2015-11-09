import os
import sys
import logging
import importlib
from argparse import ArgumentParser

from .colors import color_msg


class BaseCommand:
    """
    """
    usage = "yawf %(prog)s [options]"
    description = None
    logger = logging.getLogger(__name__)

    def __init__(self, app=None):
        this_file = sys.modules[type(self).__module__].__file__.rsplit("/", 1)
        self.name = os.path.splitext(this_file[-1])[0]
        self.parser = ArgumentParser(
            prog=sys.argv[1],
            usage=None if self.usage is None else\
                    color_msg("okblue", self.usage.strip()),
            description=None if self.description is None else\
                    color_msg("okgreen", self.description.strip()),
            epilog=None if self.__doc__ is None else\
                    color_msg("bold", self.__doc__.strip())
            )
        self.add_arguments(self.parser)
        self.app = app

    def add_arguments(self, parser):  # pragma: no cover
        pass

    def run_command(self, argv):
        namespace = self.parser.parse_args(argv)
        self.handle(namespace)

    def handle(self, options):  # pragma: no cover
        raise NotImplementedError

    def console_log(self, *msgs, color="okblue"):  # pragma: no cover
        msg = color_msg(color, *msgs)
        print(msg)

    def log(self, *msgs, level=logging.INFO):  # pragma: no cover
        self.logger.log(level, " ".join(msgs))
