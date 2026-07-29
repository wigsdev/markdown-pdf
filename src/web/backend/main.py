"""FastAPI backend for MDPDF web interface.

Provides REST API for converting Markdown to PDF,
serving the web frontend, and listing available themes.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from mdpdf import __version__
from mdpdf.config import AVAILABLE_THEMES, ConversionConfig
from mdpdf.converter import Converter
from mdpdf.exceptions import MdpdfError

from .schemas import HealthResponse, StyleInfo

logger = logging.getLogger(__name__)

# Configuration
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MDPDF_MAX_UPLOAD_MB", "10"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_ORIGINS = os.environ.get(
    "MDPDF_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

app = FastAPI(
    title="MDPDF Web",
    description="Convert Markdown to styled PDF documents",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ============================================================
# API Endpoints
# ============================================================

THEME_DESCRIPTIONS = {
    "default": "Clean, professional, light background",
    "monokai": "Dark theme with vibrant colors",
    "github": "GitHub-style dark code blocks",
    "solarized-dark": "Solarized color scheme (dark)",
    "solarized-light": "Solarized color scheme (light)",
}


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=__version__)


@app.get("/api/styles", response_model=list[StyleInfo])
async def list_styles() -> list[StyleInfo]:
    """Get available syntax highlighting themes."""
    return [
        StyleInfo(
            name=theme,
            description=THEME_DESCRIPTIONS.get(theme, ""),
        )
        for theme in AVAILABLE_THEMES
    ]


@app.post("/api/convert")
async def convert_markdown(
    file: Annotated[UploadFile | None, File()] = None,
    content: Annotated[str | None, Form()] = None,
    style: Annotated[str, Form()] = "default",
    toc: Annotated[bool, Form()] = True,
    toc_level: Annotated[int, Form()] = 3,
) -> Response:
    """Convert Markdown content or file to PDF.

    Accepts either a file upload or raw content as form field.
    Returns the generated PDF as a downloadable file.
    """
    # Get markdown content
    if file is not None:
        try:
            raw = await file.read()
            if len(raw) > MAX_UPLOAD_SIZE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {MAX_UPLOAD_SIZE_MB}MB",
                )
            markdown_content = raw.decode("utf-8")
            markdown_content = markdown_content.replace("\r\n", "\n").replace("\r", "\n")
            filename = Path(file.filename or "document").stem
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {e}") from e
    elif content is not None:
        if len(content.encode("utf-8")) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Content too large. Maximum size: {MAX_UPLOAD_SIZE_MB}MB",
            )
        markdown_content = content.replace("\r\n", "\n").replace("\r", "\n")
        filename = "document"
    else:
        raise HTTPException(status_code=400, detail="Either 'file' or 'content' must be provided")

    if not markdown_content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    # Convert
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "input.md"
            output_file = temp_path / "output.pdf"

            input_file.write_text(markdown_content, encoding="utf-8")

            config = ConversionConfig()
            config.style.theme = style
            config.style.toc = toc
            config.style.toc_level = toc_level

            converter = Converter(config)
            converter.convert(input_file, output_file)

            if not output_file.exists():
                raise HTTPException(status_code=500, detail="PDF file was not created")

            pdf_bytes = output_file.read_bytes()

            if len(pdf_bytes) == 0:
                raise HTTPException(status_code=500, detail="Generated PDF is empty")

            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}.pdf"',
                    "Content-Length": str(len(pdf_bytes)),
                },
            )

    except MdpdfError as e:
        logger.error("Conversion error: %s", e)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}") from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e


# ============================================================
# Static Files & Frontend
# ============================================================

_BACKEND_DIR = Path(__file__).parent
_FRONTEND_DIR = _BACKEND_DIR.parent / "frontend"


@app.get("/")
async def serve_frontend() -> FileResponse:
    """Serve the main frontend page."""
    index_path = _FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path)


# Mount static files if frontend directory exists
if _FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")
