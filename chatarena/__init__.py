import os

ROOT_DIR = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + os.path.sep
)
EXAMPLES_DIR = os.path.join(ROOT_DIR, "examples")

__version__ = "0.1.13"
