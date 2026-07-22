"""Request/response schemas exposed by the FastAPI routes."""
from pydantic import BaseModel, Field

from app.schemas.evaluation_schema import EvaluationReport
from app.schemas.resume_schema import GeneratedResume
from app.schemas.validation_schema import ValidationReport


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    saved_path: str
    size_mb: float


class GenerateResumeRequest(BaseModel):
    resume_file_id: str
    jd_file_id: str
    user_notes: str = ""
    template: str = "ats"


class GenerateResumeResponse(BaseModel):
    session_id: str
    resume: GeneratedResume
    validation: ValidationReport
    evaluation: EvaluationReport


class EvaluationRequest(BaseModel):
    session_id: str


class RenderRequest(BaseModel):
    session_id: str
    export_format: str = Field(default="pdf", pattern="^(pdf|docx|html)$")
    template: str = "ats"


class RenderResponse(BaseModel):
    session_id: str
    export_format: str
    file_path: str


class HealthResponse(BaseModel):
    status: str = "ok"
    app_name: str
    version: str = "1.0.0"
