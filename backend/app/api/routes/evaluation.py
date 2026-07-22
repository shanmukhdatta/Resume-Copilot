"""Evaluation retrieval endpoint for an already-generated session."""
from fastapi import APIRouter, HTTPException

from app.schemas.api_schema import EvaluationRequest
from app.schemas.evaluation_schema import EvaluationReport
from app.services.evaluation_service import SessionNotFoundError, get_evaluation

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("", response_model=EvaluationReport)
async def evaluate(request: EvaluationRequest) -> EvaluationReport:
    try:
        return get_evaluation(request.session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
