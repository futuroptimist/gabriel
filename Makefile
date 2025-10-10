.PHONY: preview lint test

preview:
python -m gabriel.viewer

lint:
	pre-commit run --all-files

test:
	pytest --cov=gabriel --cov-report=term-missing
