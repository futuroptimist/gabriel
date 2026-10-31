"""Command-line interface and ergonomic shims for Gabriel."""

from __future__ import annotations

import argparse
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

from .. import arithmetic
from .. import secrets as secrets_module
from ..inference import (
    DEFAULT_LOCAL_CONTEXT,
    DEFAULT_LOCAL_MAX_TOKENS,
    DEFAULT_LOCAL_TEMPERATURE,
    DEFAULT_LOCAL_TOP_P,
    InferenceError,
    parse_metadata,
    run_inference,
)
from ..ingestion import collect_repository_commits
from ..secrets import delete_secret, get_secret, read_secret_from_input, store_secret
from .viewer import DEFAULT_HOST, DEFAULT_PORT, serve_viewer

SECRET_CMD_STORE = "store"  # nosec B105 - CLI command name  # pragma: allowlist secret
SECRET_CMD_GET = "get"  # nosec B105 - CLI command name  # pragma: allowlist secret
SECRET_CMD_DELETE = "delete"  # nosec B105 - CLI command name  # pragma: allowlist secret

__all__ = [
    "SECRET_CMD_STORE",
    "SECRET_CMD_GET",
    "SECRET_CMD_DELETE",
    "main",
]


def main(argv: list[str] | None = None) -> None:
    """Run arithmetic, viewer, and secret management helpers from the command line."""
    parser = argparse.ArgumentParser(description="Gabriel utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_binary(name: str) -> None:
        """Register a binary arithmetic command named ``name``."""
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

    viewer_parser = subparsers.add_parser("viewer", help="Serve the WebGL viewer")
    viewer_parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host interface to bind (default: {DEFAULT_HOST})",
    )
    viewer_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to bind the server (default: {DEFAULT_PORT})",
    )
    viewer_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the default web browser when serving the viewer",
    )

    infer_parser = subparsers.add_parser(
        "infer",
        help="Run prompt inference using a local model or token.place relay",
    )
    infer_parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt text; omit to read from stdin",
    )
    infer_parser.add_argument(
        "--mode",
        choices=("local", "relay"),
        help="Inference mode to use (defaults to local when GABRIEL_MODEL_PATH is set)",
    )
    infer_parser.add_argument(
        "--model-path",
        type=Path,
        help="Path to the local GGUF model (defaults to $GABRIEL_MODEL_PATH)",
    )
    infer_parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_LOCAL_MAX_TOKENS,
        help="Maximum tokens to generate in local mode (default: %(default)s)",
    )
    infer_parser.add_argument(
        "--temperature",
        type=float,
        help="Sampling temperature (defaults to 0.2 for local mode)",
    )
    infer_parser.add_argument(
        "--top-p",
        type=float,
        default=DEFAULT_LOCAL_TOP_P,
        help="Top-p nucleus sampling value for local mode (default: %(default)s)",
    )
    infer_parser.add_argument(
        "--n-ctx",
        type=int,
        default=DEFAULT_LOCAL_CONTEXT,
        help="Context window for local llama.cpp inference (default: %(default)s)",
    )
    infer_parser.add_argument(
        "--n-threads",
        type=int,
        help="Thread count override for local inference",
    )
    infer_parser.add_argument(
        "--relay-url",
        help="Base URL for the token.place relay (required for relay mode)",
    )
    infer_parser.add_argument(
        "--api-key",
        help="API key for the token.place relay",
    )
    infer_parser.add_argument(
        "--model",
        dest="relay_model",
        help="Model identifier to request from the relay",
    )
    infer_parser.add_argument(
        "--metadata",
        help="JSON object to attach as metadata for relay requests",
    )
    infer_parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds for relay mode (default: %(default)s)",
    )

    crawl_parser = subparsers.add_parser(
        "crawl",
        help="Collect commit metadata across Git repositories",
    )
    crawl_parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to scan; defaults to the current working directory",
    )
    crawl_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of commits to capture per repository (default: 20)",
    )
    crawl_parser.add_argument(
        "--output",
        type=Path,
        help="Optional file path to write JSON results",
    )
    crawl_parser.add_argument(
        "--redact-emails",
        action="store_true",
        help="Exclude author email addresses from the JSON output",
    )

    args = parser.parse_args(argv)

    funcs = {
        "add": arithmetic.add,
        "subtract": arithmetic.subtract,
        "multiply": arithmetic.multiply,
        "divide": arithmetic.divide,
        "power": arithmetic.power,
        "modulo": arithmetic.modulo,
        "floordiv": arithmetic.floordiv,
    }

    if args.command == "sqrt":
        print(arithmetic.sqrt(args.a))
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

    if args.command == "viewer":
        serve_viewer(host=args.host, port=args.port, open_browser=not args.no_browser)
        return

    if args.command == "infer":
        prompt = args.prompt
        if prompt is None:
            prompt = sys.stdin.read()
        if not prompt:
            raise SystemExit("Prompt text is required for inference.")

        selected_mode = args.mode
        if selected_mode is None:
            selected_mode = "local" if "GABRIEL_MODEL_PATH" in os.environ else "relay"

        try:
            metadata = parse_metadata(args.metadata)
        except InferenceError as exc:
            raise SystemExit(str(exc)) from exc

        if selected_mode == "local":
            temperature = (
                args.temperature if args.temperature is not None else DEFAULT_LOCAL_TEMPERATURE
            )
            try:
                result = run_inference(
                    prompt,
                    mode="local",
                    model_path=args.model_path,
                    max_tokens=args.max_tokens,
                    temperature=temperature,
                    top_p=args.top_p,
                    n_ctx=args.n_ctx,
                    n_threads=args.n_threads,
                )
            except InferenceError as exc:
                raise SystemExit(str(exc)) from exc
            print(result.text)
            return

        if selected_mode == "relay":
            if not args.relay_url:
                raise SystemExit("--relay-url is required when mode is relay.")
            try:
                result = run_inference(
                    prompt,
                    mode="relay",
                    base_url=args.relay_url,
                    api_key=args.api_key,
                    model=args.relay_model,
                    temperature=args.temperature,
                    metadata=metadata,
                    timeout=args.timeout,
                )
            except InferenceError as exc:
                raise SystemExit(str(exc)) from exc
            print(result.text)
            return

        raise SystemExit(f"Unsupported inference mode: {selected_mode}")

    if args.command == "crawl":
        repo_paths = args.paths or [Path.cwd()]
        try:
            summaries = collect_repository_commits(
                repo_paths,
                limit=args.limit,
                redact_emails=args.redact_emails,
            )
        except (FileNotFoundError, NotADirectoryError, ValueError, RuntimeError) as exc:
            raise SystemExit(str(exc)) from exc

        payload = [summary.to_dict() for summary in summaries]
        rendered = json.dumps(payload, indent=2)
        if args.output:
            args.output.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
        return

    print(funcs[args.command](args.a, args.b))


# Backwards compatibility exports for existing imports expecting ``gabriel.utils``
_env_secret_key = secrets_module._env_secret_key
_read_secret_from_input = secrets_module._read_secret_from_input

__all__.extend(
    [
        "_env_secret_key",
        "_read_secret_from_input",
    ]
)
