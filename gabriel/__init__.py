"""Core utilities for the Gabriel project."""

from __future__ import annotations

from .arithmetic import add, divide, floordiv, modulo, multiply, power, sqrt, subtract
from .secrets import delete_secret, get_secret, store_secret

SUPPORTED_PYTHON_VERSIONS = ("3.10", "3.11")

__all__ = [
    "add",
    "subtract",
    "multiply",
    "divide",
    "power",
    "modulo",
    "floordiv",
    "sqrt",
    "store_secret",
    "get_secret",
    "delete_secret",
    "SUPPORTED_PYTHON_VERSIONS",
]
