# Multi-stage Dockerfile for Ragdex
# Supports external Vector DB, Document Library, and Logs

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CHROMA_TELEMETRY=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core tools
    curl \
    git \
    # PDF processing
    ghostscript \
    tesseract-ocr \
    tesseract-ocr-eng \
    ocrmypdf \
    poppler-utils \
    # Document conversion
    libreoffice \
    calibre \
    # Python build dependencies
    build-essential \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash ragdex

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=ragdex:ragdex . /app/

# Install Python dependencies (doc-support extras included since LibreOffice is
# installed).
#
# ARM-only stability workarounds: under Docker Desktop's ARM virtualization on
# Apple Silicon, two native libraries execute illegal instructions (SIGILL) and
# take down every service that loads the RAG stack:
#   1. the default linux/aarch64 torch wheel pulls CUDA libs (cuda-toolkit,
#      nvidia-cublas, cuda-bindings) that both bloat the image ~2-3GB and SIGILL
#      at import  -> install CPU-only torch first so it satisfies torch>=1.11.0.
#   2. cryptography 43+ (OpenSSL 3.x backend) SIGILLs on import (e.g. via pypdf)
#      -> constrain to <43.
# These do NOT occur on amd64, so that path uses the default wheels — which also
# avoids a build-time dependency on download.pytorch.org (blocked on some CI
# runners) and keeps the arm64 workarounds out of x86 images.
RUN set -eux; \
    if [ "$(dpkg --print-architecture)" = "arm64" ]; then \
        pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu; \
        pip install --no-cache-dir -e ".[doc-support]" "cryptography<43"; \
    else \
        pip install --no-cache-dir -e ".[doc-support]"; \
    fi

# Create directories for external mounts
RUN mkdir -p /data/chroma_db /data/documents /data/logs && \
    chown -R ragdex:ragdex /data

# Switch to non-root user
USER ragdex

# Set default environment variables for data directories
ENV PERSONAL_LIBRARY_DB_PATH=/data/chroma_db \
    PERSONAL_LIBRARY_DOC_PATH=/data/documents \
    PERSONAL_LIBRARY_LOGS_PATH=/data/logs

# Expose web dashboard port
EXPOSE 8888

# Default command (can be overridden)
CMD ["ragdex-web"]
