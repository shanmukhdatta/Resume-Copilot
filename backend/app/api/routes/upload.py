"""Resume and Job Description upload endpoints."""
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.validators.upload_validators import read_and_validate_upload
from app.schemas.api_schema import UploadResponse
from app.services.storage_service import FileTooLargeError, UnsupportedFileError, store_upload
from app.utils.constants import SUPPORTED_JD_EXTENSIONS, SUPPORTED_RESUME_EXTENSIONS

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/resume", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)) -> UploadResponse:
    content = await read_and_validate_upload(file)
    try:
        result = store_upload(content, file.filename, "resume", SUPPORTED_RESUME_EXTENSIONS)
    except (UnsupportedFileError, FileTooLargeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UploadResponse(**result)


@router.post("/jd", response_model=UploadResponse)
async def upload_jd(file: UploadFile = File(...)) -> UploadResponse:
    content = await read_and_validate_upload(file)
    try:
        result = store_upload(content, file.filename, "jd", SUPPORTED_JD_EXTENSIONS)
    except (UnsupportedFileError, FileTooLargeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UploadResponse(**result)
