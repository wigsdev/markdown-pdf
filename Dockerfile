# MDPDF - Markdown to PDF Converter
# Multi-stage build: system deps + app install

FROM python:3.13-slim AS base

# System dependencies for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libffi-dev \
    fonts-liberation \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for Mermaid CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Mermaid CLI globally
RUN npm install -g @mermaid-js/mermaid-cli

# ============================================================
# Application
# ============================================================
WORKDIR /app

# Copy and install package
COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir ".[web]"

# Environment
ENV MDPDF_ALLOWED_ORIGINS="*"
ENV MDPDF_MAX_UPLOAD_MB="10"

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run uvicorn pointing to the app source directly
CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/src"]
