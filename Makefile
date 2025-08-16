.PHONY: preview lint test

preview:
	python -m http.server 8000 &
	python -m webbrowser http://localhost:8000/viewer/

lint:
	pre-commit run --all-files

test:
	pytest --cov=gabriel --cov-report=term-missing
