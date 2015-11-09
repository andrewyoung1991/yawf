from ..base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--plain",
            action="store_true",
            help="use the plain python shell.",
            )

        parser.add_argument(
            "--interface",
            choices=["ipython", "bpython"],
            default="bpython",
            help="use the plain python shell.",
            )

    def handle(self, options):
        if options.plain:
            return self.load_plain(app=self.app, settings=self.app.settings)

        interface = getattr(self, "load_{}".format(options.interface))
        interface(app=self.app, settings=self.app.settings)

    @staticmethod
    def load_plain(app, settings):  # pragma: no cover
        import code

        new_vars = globals()
        new_vars.update(locals())
        new_vars.update({
            "settings": settings,
            "app": app
            })

        try:
            import readline
            import rlcompleter
        except ImportError:
            pass
        else:
            readline.set_completer(rlcompleter.Completer(new_vars).complete)
            readline.parse_and_bind("tab: complete")
        shell = code.InteractiveConsole(new_vars)
        shell.interact()

    @staticmethod
    def load_bpython(app, settings):  # pragma: no cover
        import bpython
        bpython.embed(locals_={"app": app, "settings": settings})

    @staticmethod
    def load_ipython(app, settings):  # pragma: no cover
        from IPython import start_ipython
        start_ipython(argv=[], user_ns={"app": app, "settings": settings})
