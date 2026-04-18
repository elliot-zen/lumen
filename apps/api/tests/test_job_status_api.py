from lumen_api.models import NoteJob


def test_get_job_returns_current_status_and_error_fields(client, sqlite_session):
    job = NoteJob(
        dedupe_key="job-1",
        note_type="learning_note",
        status="retryable",
        raw_payload={
            "type": "learning_note",
            "topic": "ES",
            "chapter_title": "Generators",
            "what_i_learned": ["yield pauses execution"],
            "questions": ["How does yield* compose iterators?"],
        },
        platform_name="obsidian",
        retry_count=2,
        last_error="transient failure",
    )
    sqlite_session.add(job)
    sqlite_session.commit()

    response = client.get(f"/jobs/{job.id}")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": job.id,
        "status": "retryable",
        "retry_count": 2,
        "note_path": None,
        "last_error": "transient failure",
    }


def test_get_job_returns_404_for_missing_job(client):
    response = client.get("/jobs/999999")

    assert response.status_code == 404
