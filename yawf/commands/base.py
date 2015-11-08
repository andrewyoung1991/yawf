import os
import sys
from argparse import ArgumentParser


class OptionsProxy(dict):
    def __init__(self, **options):
        super().__init__(**options)

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class BaseCommand:
    description = None

    def __init__(self):
        this_file = sys.modules[type(self).__module__].__file__.rsplit("/", 1)
        self.name = os.path.splitext(this_file[-1])[0]
        self.parser = ArgumentParser()
        self.add_arguments(self.parser)

    def add_arguments(self, parser):  # pragma: no cover
        pass

    def run_command(self, argv):
        args = self.parser.parse_args(argv)
        self(**vars(args))

    def __call__(self, **kwargs):
        # shortcut for calling this command in code
        kwargs = OptionsProxy(**kwargs)
        return self.handle(kwargs)

    def handle(self, options):  # pragma: no cover
        raise NotImplementedError
