"""Pydantic models for the web API."""

from __future__ import annotations

from pydantic import BaseModel


class StyleInfo(BaseModel):
    """Information about an available theme."""

    name: str
    description: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
