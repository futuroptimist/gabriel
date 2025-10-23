.PHONY: preview lint test spell links docs

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

docs:
	mkdocs build --strict
