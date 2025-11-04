ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS builder
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

FROM python:${PYTHON_VERSION}-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
RUN python -m pip install --no-cache-dir --upgrade pip
COPY . .
RUN useradd -m appuser
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["python"]
