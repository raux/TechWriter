"""Validate router - consistency checking following on_check protocol."""
from fastapi import APIRouter, HTTPException
from typing import List
from backend.models import ValidateRequest, ValidationResult, ConsistencyIssue
from backend.services import file_service, consistency_service

router = APIRouter(prefix="/projects/{project_name}/validate", tags=["validate"])


@router.post("/section", response_model=ValidationResult)
async def validate_section(project_name: str, request: ValidateRequest):
    """
    Validate a section following the on_check protocol:
    1. Compare target section against Introduction and RQs
    2. Return list of conceptual inconsistencies
    """
    section_content = await file_service.read_section(project_name, request.section_name)
    if section_content is None:
        raise HTTPException(status_code=404, detail=f"Section '{request.section_name}' not found")

    rqs_content = await file_service.read_section(project_name, "rqs") or ""
    introduction_content = await file_service.read_section(project_name, "introduction")

    issues = consistency_service.validate_section_against_rqs(
        section_content=section_content,
        rqs_content=rqs_content,
        introduction_content=introduction_content,
        section_name=request.section_name,
    )

    return ValidationResult(
        section_name=request.section_name,
        issues=issues,
        consistency_issues=[],
    )


@router.post("/consistency", response_model=List[ConsistencyIssue])
async def check_consistency(project_name: str):
    """
    Cross-file terminology consistency check.
    Scans all sections for conflicting use of glossary terms.
    """
    section_names = await file_service.list_sections(project_name)

    sections: dict = {}
    for name in section_names:
        content = await file_service.read_section(project_name, name)
        if content:
            sections[name] = content

    glossary_content = sections.get("glossary", "")
    glossary_terms = consistency_service.extract_terms_from_glossary(glossary_content)

    issues = consistency_service.check_terminology_consistency(sections, glossary_terms)
    return issues
