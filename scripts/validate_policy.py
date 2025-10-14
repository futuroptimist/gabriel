#!/usr/bin/env python3
"""Validate ``llm_policy.yaml`` definitions for repository guardrails."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gabriel.policy import (
    PolicyValidationError,
    load_policy_document,
    validate_policy_document,
)


def _validate_path(path: Path, *, strict_warnings: bool) -> int:
    try:
        document = load_policy_document(path)
    except PolicyValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    result = validate_policy_document(document)
    exit_code = 0

    if result.errors:
        for message in result.errors:
            print(f"ERROR: {path}: {message}", file=sys.stderr)
        exit_code = 1

    if result.warnings:
        for message in result.warnings:
            stream = sys.stderr if strict_warnings else sys.stdout
            prefix = "ERROR" if strict_warnings else "WARNING"
            print(f"{prefix}: {path}: {message}", file=stream)
        if strict_warnings:
            exit_code = 1

    if exit_code == 0:
        print(f"OK: {path} is valid")

    return exit_code


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and validate each requested policy file."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate llm_policy.yaml files to ensure command allow-lists and validators "
            "follow repository guardrails."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Paths to policy files (defaults to ./llm_policy.yaml).",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Treat warnings as errors and exit non-zero when any are encountered.",
    )

    args = parser.parse_args(argv)

    paths = args.paths or [Path("llm_policy.yaml")]
    exit_code = 0
    for path in paths:
        exit_code = max(exit_code, _validate_path(path, strict_warnings=args.strict_warnings))

    return exit_code


if __name__ == "__main__":  # pragma: no cover - exercised via CLI tests
    raise SystemExit(main())
