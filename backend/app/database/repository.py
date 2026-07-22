"""Repository pattern wrapper for persisting/reading ResumeSession rows.
No-ops gracefully when no database is configured."""
from app.database.connection import get_session_factory
from app.database.models import ResumeSession
from app.utils.json_utils import dumps


def save_session_record(session_id: str, resume_filename: str, jd_filename: str, final_resume: dict, evaluation: dict) -> None:
    factory = get_session_factory()
    if factory is None:
        return
    with factory() as db:
        record = ResumeSession(
            session_id=session_id,
            resume_filename=resume_filename,
            jd_filename=jd_filename,
            final_resume_json=dumps(final_resume),
            evaluation_json=dumps(evaluation),
        )
        db.merge(record)
        db.commit()
