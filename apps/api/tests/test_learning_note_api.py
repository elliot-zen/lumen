from lumen_api.models import NoteJob


def test_create_learning_note_accepts_valid_payload_and_persists_pending_job(client, sqlite_session):
    response = client.post(
        "/learning-note",
        json={
            "type": "learning_note",
            "topic": "ES",
            "chapter_title": "Async Iteration",
            "what_i_learned": ["for await...of iterates async iterables"],
            "questions": ["When should I prefer streams?"],
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["accepted_new"] is True
    assert body["status"] == "pending"

    jobs = sqlite_session.query(NoteJob).all()
    assert len(jobs) == 1
    assert jobs[0].status == "pending"
    assert jobs[0].raw_payload["topic"] == "ES"


def test_create_learning_note_returns_existing_job_for_duplicate_payload(client, sqlite_session):
    payload = {
        "type": "learning_note",
        "topic": "Python",
        "chapter_title": "Decorators",
        "what_i_learned": ["Decorators wrap callables"],
        "questions": ["How do wraps and descriptors interact?"],
    }

    first = client.post("/learning-note", json=payload)
    second = client.post("/learning-note", json=payload)

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["job_id"] == second.json()["job_id"]
    assert second.json()["accepted_new"] is False

    jobs = sqlite_session.query(NoteJob).all()
    assert len(jobs) == 1


def test_create_learning_note_rejects_invalid_payload(client):
    response = client.post(
        "/learning-note",
        json={
            "type": "learning_note",
            "topic": "Databases",
            "chapter_title": "Indexes",
            "what_i_learned": [],
            "questions": [],
        },
    )

    assert response.status_code == 422
