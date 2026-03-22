"""Projects router - manage projects."""
from fastapi import APIRouter
from typing import List
from backend.models import ProjectCreate
from backend.services import file_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[str])
async def list_projects():
    """List all available projects."""
    return file_service.list_projects()


@router.post("/", status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project directory."""
    file_service.ensure_project_exists(project.project_name)
    meta = {"project_name": project.project_name, "nodes": []}
    await file_service.write_canvas_meta(project.project_name, meta)
    return {"project_name": project.project_name, "status": "created"}
