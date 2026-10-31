# Offline Usage

Gabriel can run without network access by loading local language models.

1. Install [llama-cpp-python](https://github.com/abetlen/llama-cpp-python).
2. Download a compatible GGUF model file to a secure path on your machine.
3. Set the `GABRIEL_MODEL_PATH` environment variable to that file.
4. Launch Gabriel; it will load the model locally and avoid external requests.

Keep your system offline or block network access to ensure fully local inference.

You can now run local inference directly from the CLI using the unified toggle:

```bash
gabriel infer "Summarize overnight IDS alerts"
```

When `GABRIEL_MODEL_PATH` is set the command defaults to local mode. Provide `--model-path` to
override the environment variable or `--mode relay` to explicitly contact a token.place relay when
you are ready to leave offline mode.
