"""Integration tests for web API endpoints."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from web.backend.main import app


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    """Tests for GET /api/health."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient) -> None:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestStylesEndpoint:
    """Tests for GET /api/styles."""

    @pytest.mark.asyncio
    async def test_list_styles(self, client: AsyncClient) -> None:
        response = await client.get("/api/styles")
        assert response.status_code == 200
        styles = response.json()
        assert len(styles) == 5
        names = [s["name"] for s in styles]
        assert "default" in names
        assert "monokai" in names


class TestConvertEndpoint:
    """Tests for POST /api/convert."""

    @pytest.mark.asyncio
    async def test_convert_file_upload(self, client: AsyncClient, basic_md: Path) -> None:
        with basic_md.open("rb") as f:
            response = await client.post(
                "/api/convert",
                files={"file": ("test.md", f, "text/markdown")},
                data={"style": "default", "toc": "true", "toc_level": "3"},
            )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_convert_content_form(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/convert",
            data={
                "content": "# Test\n\nHello world.\n",
                "style": "default",
                "toc": "true",
                "toc_level": "3",
            },
        )
        assert response.status_code == 200
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_convert_empty_content(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/convert",
            data={"content": "", "style": "default", "toc": "true", "toc_level": "3"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_convert_no_input(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/convert",
            data={"style": "default"},
        )
        assert response.status_code == 400
