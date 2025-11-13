# Multi-stage Dockerfile for Ragdex
# Supports external Vector DB, Document Library, and Logs

FROM python:3.11-slim as base

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

# Install Python dependencies
RUN pip install --no-cache-dir -e .

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
