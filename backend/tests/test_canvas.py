"""Tests for canvas metadata endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
import shutil

from backend.main import app
from backend.services.file_service import PROJECTS_DIR

TEST_PROJECT = "test_project_canvas"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    test_path = PROJECTS_DIR / TEST_PROJECT
    if test_path.exists():
        shutil.rmtree(test_path)


@pytest.mark.asyncio
async def test_get_empty_canvas():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/projects/{TEST_PROJECT}/canvas/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["nodes"] == []


@pytest.mark.asyncio
async def test_move_node():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.patch(
            f"/projects/{TEST_PROJECT}/canvas/nodes/introduction/position",
            json={"x": 100.0, "y": 200.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["position"]["x"] == 100.0
        assert data["position"]["y"] == 200.0

        meta_resp = await client.get(f"/projects/{TEST_PROJECT}/canvas/")
        nodes = meta_resp.json()["nodes"]
        node = next(n for n in nodes if n["id"] == "introduction")
        assert node["x"] == 100.0
        assert node["y"] == 200.0
