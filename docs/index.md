# Gabriel Documentation

Welcome to the official documentation for Gabriel, the local-first security companion. This
site mirrors the repository's architecture notes, threat models, and now includes an API
reference generated directly from the Python source code.

## Quick start

- Clone the repository and run `./scripts/setup.sh` to bootstrap development tooling.
- Install documentation dependencies with `pip install -r requirements.txt`.
- Build the static site locally with `mkdocs serve` and browse to `http://127.0.0.1:8000`.
- Use the navigation sidebar to explore security guides, prompts, and the live API reference.

## API reference overview

The **API Reference** section is powered by [mkdocstrings](https://mkdocstrings.github.io/)
so the rendered pages stay in sync with docstrings and type annotations. Each module listed in
the navigation exposes the same helpers you import in Python code. Regenerate the site after
updating the codebase to verify that signatures and documentation render as expected.

## Deployment

Continuous integration now builds the MkDocs site on every pull request, and pushes the rendered
HTML to GitHub Pages whenever changes merge into `main`. Check the Actions tab for the
"Deploy MkDocs Site" workflow to confirm the publication status.
