import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gabriel.utils import greet  # noqa: E402


def test_greet():
    assert greet('World') == 'Hello, World!'
