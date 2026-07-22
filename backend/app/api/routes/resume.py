"""Resume generation and retrieval endpoints -- the core pipeline
trigger, wrapping the full LangGraph workflow."""
from fastapi import APIRouter, HTTPException

from app.schemas.api_schema import GenerateResumeRequest, GenerateResumeResponse
from app.services.parser_service import resolve_upload_path
from app.services.resume_service import generate_resume

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/generate", response_model=GenerateResumeResponse)
async def generate(request: GenerateResumeRequest) -> GenerateResumeResponse:
    resume_path = resolve_upload_path(request.resume_file_id, "resume")
    jd_path = resolve_upload_path(request.jd_file_id, "jd")

    if not resume_path:
        raise HTTPException(status_code=404, detail="Resume file not found. Upload it first.")
    if not jd_path:
        raise HTTPException(status_code=404, detail="Job description file not found. Upload it first.")

    final_state = await generate_resume(
        resume_path=resume_path,
        jd_path=jd_path,
        user_notes=request.user_notes,
        template=request.template,
    )

    return GenerateResumeResponse(
        session_id=final_state.metadata.session_id,
        resume=final_state.final_resume,
        validation=final_state.validation,
        evaluation=final_state.evaluation,
    )
