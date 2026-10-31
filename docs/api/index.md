# Gabriel API Reference

Gabriel exposes typed helpers for analysis, phishing detection, and secure storage. The sections
below render documentation directly from the source tree so you can review signatures and
docstrings without leaving the browser.

Run `python scripts/build_sphinx_docs.py --output docs/_build/sphinx` to generate an accompanying
Sphinx HTML reference at `docs/_build/sphinx/index.html`. Copy it into `site/sphinx/` after running
`mkdocs build` to publish the rendered pages with the rest of the documentation.

## Analysis recommendations

::: gabriel.analysis.recommendations
    handler: python
    options:
      show_source: false
      show_if_no_docstring: false
      filters:
        - "!^_"

## Phishing heuristics

::: gabriel.analysis.phishing
    handler: python
    options:
      show_source: false
      show_if_no_docstring: false
      filters:
        - "!^_"

## Secret storage

::: gabriel.common.secret_store
    handler: python
    options:
      show_source: false
      show_if_no_docstring: false
      filters:
        - "!^_"
