"""Generate router - LLM-powered section generation following on_generate protocol."""
from fastapi import APIRouter, HTTPException
from backend.models import GenerateRequest
from backend.services import file_service, llm_service

router = APIRouter(prefix="/projects/{project_name}/generate", tags=["generate"])


@router.post("/")
async def generate_section(project_name: str, request: GenerateRequest):
    """
    Generate section content following the on_generate protocol:
    1. Query the RQs node
    2. Query the Glossary node
    3. Synthesize new Markdown content via LLM
    """
    rqs_content = await file_service.read_section(project_name, "rqs")
    glossary_content = await file_service.read_section(project_name, "glossary")

    try:
        content = await llm_service.generate_section(
            section_type=request.section_type,
            section_name=request.section_name,
            rqs_content=rqs_content,
            glossary_content=glossary_content,
            additional_context=request.additional_context,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM generation failed: {str(e)}")

    await file_service.write_section(project_name, request.section_name, content)

    meta = await file_service.read_canvas_meta(project_name)
    nodes = meta.get("nodes", [])
    existing_ids = {n.get("id") for n in nodes}
    if request.section_name not in existing_ids:
        offset = len(nodes) * 250
        nodes.append({
            "id": request.section_name,
            "section_name": request.section_name,
            "section_type": request.section_type,
            "x": offset % 1000,
            "y": (offset // 1000) * 200,
            "width": 200,
            "height": 100,
        })
        meta["nodes"] = nodes
        await file_service.write_canvas_meta(project_name, meta)

    return {"section_name": request.section_name, "status": "generated", "content_length": len(content)}
