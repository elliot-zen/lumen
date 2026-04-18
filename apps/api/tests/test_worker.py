from datetime import UTC, datetime, timedelta
from pathlib import Path

from lumen_api.config import Settings
from lumen_api.models import JobStatus, NoteJob
from lumen_api.services.summarizer import Summarizer
from lumen_api.services.worker import Worker
from lumen_notes_platform.obsidian import ObsidianAdapter


def test_worker_processes_pending_job_and_creates_note(sqlite_session, tmp_path: Path):
    job = NoteJob(
        dedupe_key="abc",
        note_type="learning_note",
        status=JobStatus.PENDING.value,
        raw_payload={
            "type": "learning_note",
            "topic": "ES",
            "chapter_title": "Promises",
            "what_i_learned": ["Promises wrap async results"],
            "questions": ["When to use allSettled?"],
        },
        platform_name="obsidian",
    )
    sqlite_session.add(job)
    sqlite_session.commit()

    worker = Worker(
        sqlite_session,
        ObsidianAdapter(tmp_path),
        summarizer=Summarizer(settings=Settings()),
    )
    processed = worker.process_next()

    assert processed is not None
    assert processed.status == JobStatus.SUCCEEDED.value
    assert processed.note_path == "ES/Promises.md"
    assert processed.last_stdout == ""
    assert processed.last_stderr == ""
    assert (tmp_path / "ES" / "Promises.md").exists()


def test_worker_recovers_stale_processing_jobs(sqlite_session):
    stale = NoteJob(
        dedupe_key="stale",
        note_type="learning_note",
        status=JobStatus.PROCESSING.value,
        raw_payload={
            "type": "learning_note",
            "topic": "Python",
            "chapter_title": "Asyncio",
            "what_i_learned": ["await yields control"],
            "questions": ["How does gather cancel?"],
        },
        platform_name="obsidian",
        processing_started_at=datetime.now(UTC) - timedelta(hours=1),
    )
    sqlite_session.add(stale)
    sqlite_session.commit()

    worker = Worker(
        sqlite_session,
        ObsidianAdapter(sqlite_session.bind.url.database or "."),
        summarizer=Summarizer(settings=Settings()),
    )
    recovered = worker.recover_stale_jobs(stale_after_seconds=1)

    sqlite_session.refresh(stale)
    assert recovered == 1
    assert stale.status == JobStatus.RETRYABLE.value
