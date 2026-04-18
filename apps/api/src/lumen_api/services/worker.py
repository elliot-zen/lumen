from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from lumen_api.models import JobStatus, NoteJob
from lumen_api.store import JobStore
from lumen_api.services.markdown_renderer import render_learning_note_markdown
from lumen_api.services.summarizer import Summarizer
from lumen_domain.learning_notes import LearningNoteRequest
from lumen_notes_platform.contracts import NotesPlatformAdapter


class Worker:
    def __init__(
        self,
        session: Session,
        notes_platform: NotesPlatformAdapter,
        summarizer: Summarizer | None = None,
    ):
        self.session = session
        self.store = JobStore(session)
        self.notes_platform = notes_platform
        self.summarizer = summarizer or Summarizer()

    def recover_stale_jobs(self, stale_after_seconds: int) -> int:
        return self.store.stale_processing_to_retryable(stale_after_seconds)

    def process_next(self) -> NoteJob | None:
        job = self.session.scalar(self.store.build_claim_query())
        if job is None:
            self.session.rollback()
            return None

        job.status = JobStatus.PROCESSING.value
        job.processing_started_at = datetime.now(UTC)
        self.session.commit()

        try:
            payload = LearningNoteRequest.model_validate(job.raw_payload)
            summary = self.summarizer.summarize(payload)
            markdown = render_learning_note_markdown(payload, summary)
            result = self.notes_platform.add(payload.topic, payload.chapter_title, markdown)
            job.summary = summary
            job.rendered_markdown = markdown
            job.note_path = result.path
            job.last_stdout = result.stdout
            job.last_stderr = result.stderr
            job.status = JobStatus.SUCCEEDED.value
            job.last_error = None
        except Exception as exc:
            job.retry_count += 1
            job.last_error = str(exc)
            job.status = JobStatus.RETRYABLE.value if job.retry_count < 3 else JobStatus.FAILED.value
        finally:
            self.session.commit()
        return job
