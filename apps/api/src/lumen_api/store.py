from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from lumen_api.models import JobStatus, NoteJob
from lumen_domain.learning_notes import LearningNoteRequest, build_dedupe_key


class JobStore:
    def __init__(self, session: Session):
        self.session = session

    def accept_learning_note(self, payload: LearningNoteRequest) -> tuple[NoteJob, bool]:
        dedupe_key = build_dedupe_key(payload)
        job = NoteJob(
            dedupe_key=dedupe_key,
            note_type=payload.type,
            status=JobStatus.PENDING.value,
            raw_payload=payload.model_dump(mode="json"),
            platform_name="obsidian",
        )
        self.session.add(job)
        try:
            self.session.commit()
            self.session.refresh(job)
            return job, True
        except IntegrityError:
            self.session.rollback()
            existing = self.session.scalar(
                select(NoteJob).where(NoteJob.dedupe_key == dedupe_key)
            )
            if existing is None:  # pragma: no cover - defensive
                raise
            return existing, False

    def stale_processing_to_retryable(self, stale_after_seconds: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(seconds=stale_after_seconds)
        jobs = self.session.scalars(
            select(NoteJob).where(
                NoteJob.status == JobStatus.PROCESSING.value,
                NoteJob.processing_started_at < cutoff,
            )
        ).all()
        for job in jobs:
            job.status = JobStatus.RETRYABLE.value
            job.last_error = "Recovered stale processing job"
        self.session.commit()
        return len(jobs)

    def build_claim_query(self) -> Select[tuple[NoteJob]]:
        return (
            select(NoteJob)
            .where(NoteJob.status.in_([JobStatus.PENDING.value, JobStatus.RETRYABLE.value]))
            .order_by(NoteJob.created_at.asc())
            .with_for_update(skip_locked=True)
        )
