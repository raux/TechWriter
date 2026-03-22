"""Tests for generation endpoint (template fallback - no LM Studio running)."""
import pytest
from httpx import AsyncClient, ASGITransport
import shutil

from backend.main import app
from backend.services.file_service import PROJECTS_DIR

TEST_PROJECT = "test_project_generate"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    test_path = PROJECTS_DIR / TEST_PROJECT
    if test_path.exists():
        shutil.rmtree(test_path)


@pytest.mark.asyncio
async def test_generate_introduction():
    """Generate introduction section using template fallback."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/projects/{TEST_PROJECT}/generate/",
            json={
                "section_type": "introduction",
                "section_name": "introduction",
                "additional_context": "",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["section_name"] == "introduction"
        assert data["content_length"] > 0

        get_resp = await client.get(f"/projects/{TEST_PROJECT}/sections/introduction")
        assert get_resp.status_code == 200
        assert "Introduction" in get_resp.json()["content"]


@pytest.mark.asyncio
async def test_generate_with_rqs_context():
    """Generate methodology section when RQs exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            f"/projects/{TEST_PROJECT}/sections/rqs",
            json={"content": "# RQs\n\n## RQ1\nWhat is the accuracy?"},
        )
        await client.post(
            f"/projects/{TEST_PROJECT}/sections/glossary",
            json={"content": "# Glossary\n\n| Term | Definition |\n|------|------------|\n| Algorithm A | A sorting algorithm |"},
        )

        resp = await client.post(
            f"/projects/{TEST_PROJECT}/generate/",
            json={
                "section_type": "methodology",
                "section_name": "methodology_rq1",
                "additional_context": "",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["section_name"] == "methodology_rq1"

        meta_resp = await client.get(f"/projects/{TEST_PROJECT}/canvas/")
        nodes = meta_resp.json()["nodes"]
        node_ids = [n["id"] for n in nodes]
        assert "methodology_rq1" in node_ids
