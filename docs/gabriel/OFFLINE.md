# Offline Usage

Gabriel can run without network access by loading local language models.

1. Install [llama-cpp-python](https://github.com/abetlen/llama-cpp-python).
2. Download a compatible GGUF model file to a secure path on your machine.
3. Set the `GABRIEL_MODEL_PATH` environment variable to that file.
4. Launch Gabriel; it will load the model locally and avoid external requests.

Keep your system offline or block network access to ensure fully local inference.
