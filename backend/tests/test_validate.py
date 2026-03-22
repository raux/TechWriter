"""Tests for validation endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
import shutil

from backend.main import app
from backend.services.file_service import PROJECTS_DIR
from backend.services.consistency_service import (
    extract_terms_from_glossary,
    validate_section_against_rqs,
    check_terminology_consistency,
)

TEST_PROJECT = "test_project_validate"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    test_path = PROJECTS_DIR / TEST_PROJECT
    if test_path.exists():
        shutil.rmtree(test_path)


@pytest.mark.asyncio
async def test_validate_section_no_rqs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            f"/projects/{TEST_PROJECT}/sections/discussion",
            json={"content": "# Discussion\n\nSome discussion."},
        )
        resp = await client.post(
            f"/projects/{TEST_PROJECT}/validate/section",
            json={"section_name": "discussion"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert any("RQ" in issue for issue in data["issues"])


@pytest.mark.asyncio
async def test_validate_section_with_rqs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            f"/projects/{TEST_PROJECT}/sections/rqs",
            json={"content": "# RQs\n\n## RQ1\nWhat is the accuracy?\n\n## RQ2\nWhat is the efficiency?"},
        )
        await client.post(
            f"/projects/{TEST_PROJECT}/sections/methodology_rq1",
            json={"content": "# Methodology for RQ1\n\nWe use **Algorithm A** to address RQ1."},
        )
        resp = await client.post(
            f"/projects/{TEST_PROJECT}/validate/section",
            json={"section_name": "methodology_rq1"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["section_name"] == "methodology_rq1"
        assert len(data["issues"]) > 0


def test_extract_terms_from_glossary():
    glossary = "# Glossary\n\n| Term | Definition |\n|------|------------|\n| Algorithm A | A fast sorting algorithm |\n| Method B | An evaluation method |"
    terms = extract_terms_from_glossary(glossary)
    assert "Algorithm A" in terms
    assert "Method B" in terms


def test_consistency_check_flags_multi_term_sentence():
    sections = {
        "methodology": "We apply Algorithm A which is similar to Method B in this context."
    }
    glossary_terms = {"Algorithm A": "A sorting algorithm", "Method B": "An evaluation method"}
    issues = check_terminology_consistency(sections, glossary_terms)
    assert len(issues) > 0
    assert "methodology" in issues[0].found_in


def test_validate_section_new_terminology():
    issues = validate_section_against_rqs(
        section_content="# Methodology\n\nWe use **Neural Network X** to address RQ1.",
        rqs_content="# RQs\n\n## RQ1\nWhat is the accuracy?",
        introduction_content="# Introduction\n\nThis paper explores machine learning.",
        section_name="methodology",
    )
    assert any("terminology" in issue.lower() or "Neural Network X" in issue for issue in issues)
