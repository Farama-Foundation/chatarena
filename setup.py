"""Sets up the project."""

import pathlib

from setuptools import setup

CWD = pathlib.Path(__file__).absolute().parent


def get_version():
    """Gets the chatarena version."""
    path = CWD / "chatarena" / "__init__.py"
    content = path.read_text()

    for line in content.splitlines():
        if line.startswith("__version__"):
            return line.strip().split()[-1].strip().strip('"')
    raise RuntimeError("bad version data in __init__.py")


setup(name="chatarena", version=get_version())
