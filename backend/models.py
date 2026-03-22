from pydantic import BaseModel
from typing import List, Optional


class Section(BaseModel):
    name: str
    title: str
    content: str
    section_type: str


class SectionUpdate(BaseModel):
    content: str


class CanvasNode(BaseModel):
    id: str
    section_name: str
    section_type: str = ""
    x: float
    y: float
    width: float = 200.0
    height: float = 100.0


class CanvasMeta(BaseModel):
    project_name: str
    nodes: List[CanvasNode]


class GenerateRequest(BaseModel):
    section_type: str
    section_name: str
    additional_context: str = ""


class ValidateRequest(BaseModel):
    section_name: str


class MoveNodeRequest(BaseModel):
    x: float
    y: float


class ConsistencyIssue(BaseModel):
    term: str
    found_in: str
    context: str


class ValidationResult(BaseModel):
    section_name: str
    issues: List[str]
    consistency_issues: List[ConsistencyIssue]


class ProjectCreate(BaseModel):
    project_name: str
