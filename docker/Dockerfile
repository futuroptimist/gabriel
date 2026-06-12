ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim
WORKDIR /app
COPY requirements-runtime.txt pyproject.toml README.md LICENSE ./
COPY gabriel ./gabriel
RUN pip install --no-cache-dir --upgrade "setuptools>=82.0.1" "wheel>=0.46.3" && \
    pip install --no-cache-dir -r requirements-runtime.txt . && \
    (pip uninstall -y wheel || true) && \
    useradd -m appuser
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["python"]
