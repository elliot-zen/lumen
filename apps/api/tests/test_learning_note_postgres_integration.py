from fastapi.testclient import TestClient

from lumen_api.app import app
from lumen_api.db import get_db
from lumen_api.models import NoteJob


def test_postgres_accept_flow_persists_job(postgres_session):
    def override_get_db():
        yield postgres_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            response = client.post(
                "/learning-note",
                json={
                    "type": "learning_note",
                    "topic": "Databases",
                    "chapter_title": "MVCC",
                    "what_i_learned": ["MVCC keeps readers from blocking writers"],
                    "questions": ["How does vacuum affect bloat?"],
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    body = response.json()
    assert body["accepted_new"] is True

    jobs = postgres_session.query(NoteJob).all()
    assert len(jobs) == 1
    assert jobs[0].status == "pending"
    assert jobs[0].raw_payload["chapter_title"] == "MVCC"
