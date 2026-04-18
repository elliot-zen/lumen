from __future__ import annotations

from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class NoteSource(BaseModel):
    kind: str | None = None
    title: str | None = None


class LearningNoteRequest(BaseModel):
    type: Literal["learning_note"]
    topic: str = Field(min_length=1)
    chapter_title: str = Field(min_length=1)
    what_i_learned: list[str] = Field(min_length=1)
    questions: list[str] = Field(min_length=1)
    source: NoteSource | None = None

    @field_validator("what_i_learned", "questions")
    @classmethod
    def validate_non_blank_items(cls, values: list[str]) -> list[str]:
        if any(not item.strip() for item in values):
            raise ValueError("list items must be non-blank")
        return values


def build_dedupe_key(payload: LearningNoteRequest) -> str:
    normalized = {
        "type": payload.type,
        "topic": payload.topic.strip().casefold(),
        "chapter_title": payload.chapter_title.strip().casefold(),
        "what_i_learned": [item.strip() for item in payload.what_i_learned],
        "questions": [item.strip() for item in payload.questions],
    }
    digest = sha256(repr(normalized).encode("utf-8")).hexdigest()
    return digest
