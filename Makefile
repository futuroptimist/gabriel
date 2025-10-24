.PHONY: preview lint test spell links docs docs-sphinx

preview:
	python -m gabriel.ui.viewer

lint:
	pre-commit run --all-files

test:
	pytest --cov=gabriel --cov-report=term-missing

spell:
	pyspelling -c .spellcheck.yaml

links:
	lychee --config lychee.toml README.md docs

docs-sphinx:
        python scripts/build_sphinx_docs.py --output docs/_build/sphinx

docs: docs-sphinx
        mkdocs build --strict
        python scripts/build_sphinx_docs.py --output docs/_build/sphinx --site-dir site/sphinx --skip-build
