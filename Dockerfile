# MDPDF - Markdown to PDF Converter

FROM python:3.13-slim

# System dependencies for WeasyPrint + Puppeteer (Mermaid CLI)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libffi-dev \
    fonts-liberation \
    fonts-dejavu-core \
    # Puppeteer/Chromium (required by mermaid-cli)
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    libatspi2.0-0 \
    # Tools
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Mermaid CLI (downloads Chromium headless automatically)
RUN npm install -g @mermaid-js/mermaid-cli

# Application
WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir ".[web]"

# Environment
ENV MDPDF_ALLOWED_ORIGINS="*"
ENV MDPDF_MAX_UPLOAD_MB="10"
ENV PUPPETEER_SKIP_DOWNLOAD="false"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/src"]
