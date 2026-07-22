"""Tests for the ATS keyword-coverage validator."""
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume
from app.validators.ats_validator import validate_ats


def test_validate_ats_passes_with_good_coverage():
    resume = GeneratedResume(summary="Experienced Python and FastAPI backend engineer.")
    jd = ParsedJobDescription(keywords=["Python", "FastAPI"])
    passed, issues = validate_ats(resume, jd)
    assert passed is True
    assert issues == []


def test_validate_ats_fails_with_no_overlap():
    resume = GeneratedResume(summary="Experienced florist and event planner.")
    jd = ParsedJobDescription(keywords=["Kubernetes", "Golang", "gRPC", "Terraform"])
    passed, issues = validate_ats(resume, jd)
    assert passed is False
    assert len(issues) == 1
