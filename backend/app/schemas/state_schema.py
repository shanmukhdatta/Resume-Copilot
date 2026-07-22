"""The strongly-typed Shared LangGraph State.

Every node in the graph reads/writes this state. No raw dictionaries with
unknown schema are permitted -- everything is a Pydantic model.

Two fields (`metadata` and `generated_sections`) are written concurrently
during the parallel multi-agent fan-out step, so they carry explicit
LangGraph reducers that merge concurrent partial updates instead of
raising an "only one value per step" conflict.
"""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.evaluation_schema import EvaluationReport
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.planning_schema import PlanningOutput
from app.schemas.resume_schema import GeneratedResume, ParsedResume
from app.schemas.validation_schema import ValidationReport


class FileMetadata(BaseModel):
    resume_path: str = ""
    jd_path: str = ""
    resume_filename: str = ""
    jd_filename: str = ""


class GraphMetadata(BaseModel):
    session_id: str = ""
    template: str = "ats"
    current_node: str = ""
    retry_count: int = 0
    errors: list[str] = Field(default_factory=list)


class GeneratedSections(BaseModel):
    """Output slots written by each parallel agent. Each agent writes
    ONLY to its own field and never touches another agent's output."""

    summary: str = ""
    skills: list = Field(default_factory=list)
    experience: list = Field(default_factory=list)
    projects: list = Field(default_factory=list)
    education: list = Field(default_factory=list)
    certifications: list = Field(default_factory=list)
    achievements: list = Field(default_factory=list)
    links: list = Field(default_factory=list)


def merge_generated_sections(
    current: GeneratedSections, incoming: GeneratedSections
) -> GeneratedSections:
    """Reducer for concurrent parallel-agent writes: each agent only
    populates its own field and leaves the rest at their defaults, so we
    fold in any field from `incoming` that differs from the schema
    default, keeping everything else from `current`."""
    if current is None:
        return incoming
    if incoming is None:
        return current

    merged = current.model_copy(deep=True)
    defaults = GeneratedSections()
    for field_name in GeneratedSections.model_fields:
        incoming_value = getattr(incoming, field_name)
        default_value = getattr(defaults, field_name)
        if incoming_value != default_value:
            setattr(merged, field_name, incoming_value)
    return merged


def merge_metadata(current: GraphMetadata, incoming: GraphMetadata) -> GraphMetadata:
    """Reducer for concurrent parallel-agent writes to shared run
    metadata: unions error lists, keeps the highest retry_count, and
    prefers whichever current_node is non-empty."""
    if current is None:
        return incoming
    if incoming is None:
        return current

    merged = current.model_copy(deep=True)
    merged.errors = list(dict.fromkeys(current.errors + incoming.errors))
    merged.retry_count = max(current.retry_count, incoming.retry_count)
    merged.current_node = incoming.current_node or current.current_node
    merged.session_id = current.session_id or incoming.session_id
    merged.template = current.template or incoming.template
    return merged


class ResumeCopilotState(BaseModel):
    """The single shared state object threaded through the entire
    LangGraph workflow, from upload to final output."""

    files: FileMetadata = Field(default_factory=FileMetadata)
    metadata: Annotated[GraphMetadata, merge_metadata] = Field(
        default_factory=GraphMetadata
    )

    user_notes: str = ""

    resume: ParsedResume = Field(default_factory=ParsedResume)
    jd: ParsedJobDescription = Field(default_factory=ParsedJobDescription)

    planning: PlanningOutput = Field(default_factory=PlanningOutput)
    generated_sections: Annotated[GeneratedSections, merge_generated_sections] = Field(
        default_factory=GeneratedSections
    )
    final_resume: GeneratedResume = Field(default_factory=GeneratedResume)

    validation: ValidationReport = Field(default_factory=ValidationReport)
    evaluation: EvaluationReport = Field(default_factory=EvaluationReport)

    rendered_paths: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)
