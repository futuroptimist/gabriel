# WebGL Viewer Guide

Gabriel includes a lightweight WebGL viewer for exploring 3D threat models and architectural
concepts. The assets live under `gabriel/viewer_assets/` and are served as static files.

## Quick start

Use the bundled CLI helper to start a local server:

```bash
$ gabriel-viewer
Serving viewer at http://127.0.0.1:8000/index.html
Press Ctrl+C to stop.
```

The command automatically opens your default browser unless you pass `--no-browser`.

## Command-line options

- `--host`: Interface to bind. Default is `127.0.0.1` for local-only access. Use `0.0.0.0`
  to share the viewer on your LAN.
- `--port`: TCP port. Defaults to an ephemeral port selected by the OS.
- `--no-browser`: Suppress the automatic browser launch.
- `--index`: Path to open relative to the viewer directory. Defaults to `index.html`.

## Customize models

1. Place additional `.glb` or `.gltf` files in the `gabriel/viewer_assets/` directory.
2. Update `gabriel/viewer_assets/index.html` to reference your new assets. The default template loads
   `model.glb`, but you can swap in any other file that `model-viewer` supports.
3. Restart `gabriel-viewer` to serve the updated scene.

For finer control, edit `gabriel/viewer_assets/viewer.js` to adjust interaction controls, lighting,
and metadata legends. Changes are picked up on browser refresh.

## Troubleshooting

- **Port already in use** – Supply a different `--port` value (e.g., `gabriel-viewer --port 8081`).
- **Blank page** – Check the browser developer console for 404 errors. Ensure custom assets are in
  `gabriel/viewer_assets/` and referenced correctly from `index.html`.
- **No models listed** – Verify your `.glb` files include node names. The legend defaults to
  `part-<index>` when names are missing.

## Related documentation

- [Prompt catalog](../prompts/codex/README.md)
- [Threat model viewer assets](../../gabriel/viewer_assets/)
