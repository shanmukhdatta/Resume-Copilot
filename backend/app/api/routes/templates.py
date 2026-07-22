"""Endpoints for listing templates and rendering/exporting a session's
final resume."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.api_schema import RenderRequest, RenderResponse
from app.services.rendering_service import (
    SessionNotFoundError,
    UnsupportedExportFormatError,
    render_session,
)
from app.services.template_service import list_templates

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("")
async def get_templates() -> dict:
    return {"templates": list_templates()}


@router.post("/render", response_model=RenderResponse)
async def render(request: RenderRequest) -> RenderResponse:
    try:
        file_path = render_session(request.session_id, request.export_format, request.template)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnsupportedExportFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RenderResponse(session_id=request.session_id, export_format=request.export_format, file_path=file_path)


@router.get("/download/{session_id}/{export_format}")
async def download(session_id: str, export_format: str):
    try:
        file_path = render_session(session_id, export_format, "ats")
    except (SessionNotFoundError, UnsupportedExportFormatError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileResponse(file_path)
