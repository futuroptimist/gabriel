"""Build Sphinx API documentation and optionally publish it to the MkDocs site."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

try:
    from sphinx.cmd.build import build_main
except ModuleNotFoundError as exc:
    message = (
        "Sphinx is required to build the API documentation. "
        "Install it with 'pip install -r requirements.txt' or 'pip install \"gabriel[docs]\"'."
    )
    raise SystemExit(message) from exc


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the Sphinx build helper."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="docs/_build/sphinx",
        help="Directory to write the generated Sphinx HTML output.",
    )
    parser.add_argument(
        "--site-dir",
        help=(
            "Optional path (relative to the repository root) where the built HTML should be "
            "copied. Typically 'site/sphinx' after running 'mkdocs build'."
        ),
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip invoking Sphinx and only copy the previously built output.",
    )
    return parser.parse_args()


def ensure_sphinx_output(output_dir: Path, skip_build: bool) -> None:
    """Run Sphinx to produce documentation unless explicitly skipped."""
    if skip_build:
        if not output_dir.exists():
            msg = f"Cannot skip build; output directory {output_dir} is missing."
            raise FileNotFoundError(msg)
        return

    source_dir = Path("docs") / "sphinx"
    status = build_main(["-b", "html", str(source_dir), str(output_dir)])
    if status != 0:
        raise SystemExit(status)


def copy_to_site(output_dir: Path, site_dir: Path) -> None:
    """Copy the generated documentation into the MkDocs site directory."""
    site_dir.parent.mkdir(parents=True, exist_ok=True)
    if site_dir.exists():
        shutil.rmtree(site_dir)
    shutil.copytree(output_dir, site_dir)


def main() -> None:
    """Entry point for the Sphinx build helper script."""
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    output_dir = (root / args.output).resolve()
    ensure_sphinx_output(output_dir, args.skip_build)

    if args.site_dir:
        if not output_dir.exists():
            msg = f"Sphinx output directory {output_dir} does not exist."
            raise FileNotFoundError(msg)
        copy_to_site(output_dir, (root / args.site_dir).resolve())


if __name__ == "__main__":  # pragma: no cover - exercised via CLI
    main()
