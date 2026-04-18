from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status

from lumen_api.deps import get_job_store
from lumen_api.db import init_database
from lumen_api.models import NoteJob
from lumen_api.store import JobStore
from lumen_domain.learning_notes import LearningNoteRequest


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_database()
    yield

app = FastAPI(title="lumen", lifespan=lifespan)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/learning-note", status_code=status.HTTP_202_ACCEPTED)
def create_learning_note(
    payload: LearningNoteRequest,
    store: JobStore = Depends(get_job_store),
) -> dict:
    try:
        job, accepted_new = store.accept_learning_note(payload)
    except Exception as exc:  # pragma: no cover - fallback boundary
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "job_id": job.id,
        "status": job.status,
        "accepted_new": accepted_new,
        "dedupe_key": job.dedupe_key,
    }


@app.get("/jobs/{job_id}")
def get_job(job_id: int, store: JobStore = Depends(get_job_store)) -> dict:
    job = store.session.get(NoteJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "retry_count": job.retry_count,
        "note_path": job.note_path,
        "last_error": job.last_error,
    }
