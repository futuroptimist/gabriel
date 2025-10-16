# WebGL Viewer Usage

Gabriel bundles a self-contained WebGL scene under [`viewer/`](../../viewer). The assets ship with a
local copy of `@google/model-viewer` so you can explore the model without reaching out to third-party
CDNs. Use the helpers below to serve the files over HTTP when iterating on animations or materials.

## Launch from the CLI

The primary entry point is exposed through the main Gabriel CLI:

```bash
gabriel viewer --port 9000
```

This command starts a threaded HTTP server bound to `127.0.0.1:9000`, opens your default browser, and
blocks until you press `Ctrl+C`. Supply `--host 0.0.0.0` to make the viewer
available to other devices on your LAN, or add `--no-browser` when running on a headless host.

## Python module

The same helper is also available as a module:

```bash
python -m gabriel.ui.viewer --port 8001 --no-browser
```

This variant is useful for shell scripts or the `Makefile` `preview` task, which now delegates to the
module to avoid duplicating logic. A legacy shim at ``gabriel.viewer`` remains available so existing
scripts keep working during the migration.

## Automation building blocks

For bespoke workflows import the underlying helpers in Python code:

```python
from gabriel.ui.viewer import start_viewer_server

with start_viewer_server(port=0) as server:
    print("Viewer available at", server.url())
    # Run custom logic while the server is live
```

Passing `port=0` asks the operating system to pick a free port automatically. The returned server
object exposes a `url()` helper and shuts down cleanly when leaving the context manager.

These utilities keep the viewer experience entirely local and make it straightforward to integrate
with other automation, CI checks, or manual demos.

## Formatting viewer assets

Viewer JavaScript and HTML files are auto-formatted with Prettier via pre-commit. Run

```bash
npx prettier --write viewer/index.html viewer/viewer.js
```

before committing manual edits so local changes align with the repository style.

## Testing

Use the Jest suite to exercise viewer interactions in a headless DOM:

```bash
npm ci
npm run test:ci
```

The tests load `viewer.js` inside JSDOM, dispatch model events, and verify legend toggles,
explode offsets, and theme switches to catch regressions before shipping new assets.
