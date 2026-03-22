"""Tests for section CRUD endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
import shutil

from backend.main import app
from backend.services.file_service import PROJECTS_DIR

TEST_PROJECT = "test_project_sections"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    test_path = PROJECTS_DIR / TEST_PROJECT
    if test_path.exists():
        shutil.rmtree(test_path)


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_status_endpoint():
    """Status endpoint returns LM Studio connectivity info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "lm_studio" in data
    assert data["lm_studio"] in ("online", "offline")


@pytest.mark.asyncio
async def test_create_and_get_section():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/projects/{TEST_PROJECT}/sections/introduction",
            json={"content": "# Introduction\n\nThis is the introduction."},
        )
        assert resp.status_code == 201

        resp = await client.get(f"/projects/{TEST_PROJECT}/sections/introduction")
        assert resp.status_code == 200
        data = resp.json()
        assert data["section_name"] == "introduction"
        assert "Introduction" in data["content"]


@pytest.mark.asyncio
async def test_update_section():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            f"/projects/{TEST_PROJECT}/sections/rqs",
            json={"content": "# RQs\n\n## RQ1\nOriginal"},
        )
        resp = await client.put(
            f"/projects/{TEST_PROJECT}/sections/rqs",
            json={"content": "# RQs\n\n## RQ1\nUpdated"},
        )
        assert resp.status_code == 200

        resp = await client.get(f"/projects/{TEST_PROJECT}/sections/rqs")
        assert "Updated" in resp.json()["content"]


@pytest.mark.asyncio
async def test_delete_section():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            f"/projects/{TEST_PROJECT}/sections/conclusion",
            json={"content": "# Conclusion\n\nDone."},
        )
        resp = await client.delete(f"/projects/{TEST_PROJECT}/sections/conclusion")
        assert resp.status_code == 200

        resp = await client.get(f"/projects/{TEST_PROJECT}/sections/conclusion")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_sections():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for name in ["introduction", "rqs", "conclusion"]:
            await client.post(
                f"/projects/{TEST_PROJECT}/sections/{name}",
                json={"content": f"# {name}"},
            )
        resp = await client.get(f"/projects/{TEST_PROJECT}/sections/")
        assert resp.status_code == 200
        sections = resp.json()
        assert "introduction" in sections
        assert "rqs" in sections
