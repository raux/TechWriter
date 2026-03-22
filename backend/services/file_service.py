"""File service for managing project directories and section files."""
import os
import json
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any

PROJECTS_DIR = Path(__file__).parent.parent / "projects"


def get_project_path(project_name: str) -> Path:
    return PROJECTS_DIR / project_name


def get_sections_path(project_name: str) -> Path:
    return get_project_path(project_name) / "sections"


def get_canvas_meta_path(project_name: str) -> Path:
    return get_project_path(project_name) / "canvas_meta.json"


def ensure_project_exists(project_name: str) -> Path:
    project_path = get_project_path(project_name)
    sections_path = get_sections_path(project_name)
    sections_path.mkdir(parents=True, exist_ok=True)
    return project_path


async def read_section(project_name: str, section_name: str) -> Optional[str]:
    path = get_sections_path(project_name) / f"{section_name}.md"
    if not path.exists():
        return None
    async with aiofiles.open(path, "r") as f:
        return await f.read()


async def write_section(project_name: str, section_name: str, content: str) -> None:
    ensure_project_exists(project_name)
    path = get_sections_path(project_name) / f"{section_name}.md"
    async with aiofiles.open(path, "w") as f:
        await f.write(content)


async def delete_section(project_name: str, section_name: str) -> bool:
    path = get_sections_path(project_name) / f"{section_name}.md"
    if not path.exists():
        return False
    path.unlink()
    return True


async def list_sections(project_name: str) -> List[str]:
    sections_path = get_sections_path(project_name)
    if not sections_path.exists():
        return []
    return [f.stem for f in sections_path.glob("*.md")]


async def read_canvas_meta(project_name: str) -> Dict[str, Any]:
    path = get_canvas_meta_path(project_name)
    if not path.exists():
        return {"project_name": project_name, "nodes": []}
    async with aiofiles.open(path, "r") as f:
        return json.loads(await f.read())


async def write_canvas_meta(project_name: str, meta: Dict[str, Any]) -> None:
    ensure_project_exists(project_name)
    path = get_canvas_meta_path(project_name)
    async with aiofiles.open(path, "w") as f:
        await f.write(json.dumps(meta, indent=2))


def list_projects() -> List[str]:
    if not PROJECTS_DIR.exists():
        return []
    return [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()]
