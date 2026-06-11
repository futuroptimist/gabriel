ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim
WORKDIR /app
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*
COPY requirements-runtime.txt pyproject.toml README.md LICENSE ./
COPY gabriel ./gabriel
RUN pip install --no-cache-dir -r requirements-runtime.txt . && \
    pip uninstall -y wheel || true && \
    useradd -m appuser
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["python"]
