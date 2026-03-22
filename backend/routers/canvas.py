"""Canvas router - manage canvas_meta.json for node positions."""
from fastapi import APIRouter
from backend.services import file_service

router = APIRouter(prefix="/projects/{project_name}/canvas", tags=["canvas"])


@router.get("/", response_model=dict)
async def get_canvas_meta(project_name: str):
    """Get canvas metadata (node positions)."""
    meta = await file_service.read_canvas_meta(project_name)
    return meta


@router.put("/")
async def update_canvas_meta(project_name: str, meta: dict):
    """Replace the entire canvas metadata."""
    await file_service.write_canvas_meta(project_name, meta)
    return {"status": "updated"}


@router.patch("/nodes/{node_id}/position")
async def move_node(project_name: str, node_id: str, position: dict):
    """Update the (x, y) position of a specific node. Implements the 'on_move' protocol."""
    meta = await file_service.read_canvas_meta(project_name)
    nodes = meta.get("nodes", [])

    node_found = False
    for node in nodes:
        if node.get("id") == node_id:
            node["x"] = position.get("x", node.get("x", 0))
            node["y"] = position.get("y", node.get("y", 0))
            node_found = True
            break

    if not node_found:
        nodes.append({
            "id": node_id,
            "x": position.get("x", 0),
            "y": position.get("y", 0),
        })
        meta["nodes"] = nodes

    await file_service.write_canvas_meta(project_name, meta)
    return {"node_id": node_id, "status": "moved", "position": {"x": position.get("x"), "y": position.get("y")}}
