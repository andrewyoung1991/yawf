import os
import binascii
import importlib
import functools as ft
import glob
from string import Template


def generate_secret():  # pragma: no cover
    return binascii.hexlify(os.urandom(24)).decode()


def find_commands(commands_dir):  # pragma: no cover
    command_modules = os.listdir(commands_dir)
    commands = []
    for command_module in command_modules:
        if not command_module.startswith("_"):
            command, _ = os.path.splitext(command_module)
            commands.append(command)
    return commands


TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates")


def load_template(path):
    with open(path) as template_file:
        template = Template(template_file.read())
    return template


def find_template(template_dir, template_name):
    _, ext = os.path.splitext(template_name)
    pattern = os.path.join(template_dir, "**", "*" + ext)
    for path in glob.iglob(pattern, recursive=True):
        if path.endswith(template_name):
            return load_template(path)
    raise FileNotFoundError("{0} checked"
        " {1}".format(template_name, template_dir))


load_core_template = ft.partial(find_template, TEMPLATE_DIR)
