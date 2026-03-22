"""Sections router - CRUD for .md section files."""
from fastapi import APIRouter, HTTPException
from typing import List
from backend.services import file_service

router = APIRouter(prefix="/projects/{project_name}/sections", tags=["sections"])


@router.get("/", response_model=List[str])
async def list_sections(project_name: str):
    """List all section names in a project."""
    return await file_service.list_sections(project_name)


@router.get("/{section_name}", response_model=dict)
async def get_section(project_name: str, section_name: str):
    """Get the content of a specific section."""
    content = await file_service.read_section(project_name, section_name)
    if content is None:
        raise HTTPException(status_code=404, detail=f"Section '{section_name}' not found")
    return {"section_name": section_name, "content": content}


@router.post("/{section_name}", status_code=201)
async def create_section(project_name: str, section_name: str, section: dict):
    """Create a new section with initial content."""
    existing = await file_service.read_section(project_name, section_name)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Section '{section_name}' already exists")
    content = section.get("content", f"# {section_name}\n\n")
    await file_service.write_section(project_name, section_name, content)
    return {"section_name": section_name, "status": "created"}


@router.put("/{section_name}")
async def update_section(project_name: str, section_name: str, section: dict):
    """Update the content of an existing section."""
    content = section.get("content", "")
    await file_service.write_section(project_name, section_name, content)
    return {"section_name": section_name, "status": "updated"}


@router.delete("/{section_name}")
async def delete_section(project_name: str, section_name: str):
    """Delete a section."""
    deleted = await file_service.delete_section(project_name, section_name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Section '{section_name}' not found")
    return {"section_name": section_name, "status": "deleted"}
