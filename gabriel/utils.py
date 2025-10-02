"""Command-line interface and compatibility exports for Gabriel helpers."""

from __future__ import annotations

import argparse
from decimal import Decimal

from . import secrets as secrets_module
from .arithmetic import add, divide, floordiv, modulo, multiply, power, sqrt, subtract
from .secrets import delete_secret, get_secret, read_secret_from_input, store_secret

SECRET_CMD_STORE = "store"  # nosec B105 - CLI command name  # pragma: allowlist secret
SECRET_CMD_GET = "get"  # nosec B105 - CLI command name  # pragma: allowlist secret
SECRET_CMD_DELETE = "delete"  # nosec B105 - CLI command name  # pragma: allowlist secret


def main(argv: list[str] | None = None) -> None:
    """Run arithmetic and secret management helpers from the command line."""

    parser = argparse.ArgumentParser(description="Gabriel utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_binary(name: str) -> None:
        sp = subparsers.add_parser(name)
        sp.add_argument("a", type=Decimal)
        sp.add_argument("b", type=Decimal)

    for name in ("add", "subtract", "multiply", "divide", "power", "modulo", "floordiv"):
        add_binary(name)

    sqrt_parser = subparsers.add_parser("sqrt")
    sqrt_parser.add_argument("a", type=Decimal)

    secret_parser = subparsers.add_parser("secret", help="Manage stored secrets")
    secret_subparsers = secret_parser.add_subparsers(dest="secret_command", required=True)

    secret_store = secret_subparsers.add_parser(SECRET_CMD_STORE, help="Store a secret value")
    secret_store.add_argument("service", help="Service identifier for the secret")
    secret_store.add_argument("username", help="Username associated with the secret")
    secret_store.add_argument(
        "--secret",
        dest="secret",
        help="Secret value; reads from stdin or prompts when omitted",
    )

    secret_get = secret_subparsers.add_parser(SECRET_CMD_GET, help="Retrieve a stored secret")
    secret_get.add_argument("service")
    secret_get.add_argument("username")

    secret_delete = secret_subparsers.add_parser(SECRET_CMD_DELETE, help="Delete a stored secret")
    secret_delete.add_argument("service")
    secret_delete.add_argument("username")

    args = parser.parse_args(argv)

    funcs = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
        "power": power,
        "modulo": modulo,
        "floordiv": floordiv,
    }

    if args.command == "sqrt":
        print(sqrt(args.a))
        return

    if args.command == "secret":
        if args.secret_command == SECRET_CMD_STORE:
            secret_value = read_secret_from_input(args.secret)
            store_secret(args.service, args.username, secret_value)
            print("Secret stored.")
            return
        if args.secret_command == SECRET_CMD_GET:
            retrieved = get_secret(args.service, args.username)
            if retrieved is None:
                raise SystemExit("No secret stored for the requested service/user.")
            print("Secret successfully retrieved. (Value not displayed for security reasons.)")
            return
        if args.secret_command == SECRET_CMD_DELETE:
            delete_secret(args.service, args.username)
            print("Secret deleted.")
            return
        raise SystemExit("Unknown secret command.")  # pragma: no cover - argparse guards choices

    print(funcs[args.command](args.a, args.b))


# Backwards compatibility exports for existing imports expecting ``gabriel.utils``
_env_secret_key = secrets_module._env_secret_key
_read_secret_from_input = secrets_module._read_secret_from_input

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
    "read_secret_from_input",
    "_env_secret_key",
    "_read_secret_from_input",
    "SECRET_CMD_STORE",
    "SECRET_CMD_GET",
    "SECRET_CMD_DELETE",
    "main",
]


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
