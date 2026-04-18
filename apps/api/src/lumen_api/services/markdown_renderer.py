from lumen_domain.learning_notes import LearningNoteRequest


def render_learning_note_markdown(
    payload: LearningNoteRequest,
    summary: str,
) -> str:
    learned = "\n".join(f"- {item}" for item in payload.what_i_learned)
    questions = "\n".join(f"- {item}" for item in payload.questions)
    source = ""
    if payload.source:
        source = (
            "\n## Source\n"
            f"- kind: {payload.source.kind or 'unknown'}\n"
            f"- title: {payload.source.title or 'unknown'}\n"
        )
    return (
        f"# {payload.chapter_title}\n\n"
        f"## Topic\n{payload.topic}\n\n"
        f"## Summary\n{summary}\n\n"
        f"## What I Learned\n{learned}\n\n"
        f"## Questions\n{questions}\n"
        f"{source}\n"
    )
