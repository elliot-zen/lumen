from lumen_domain.learning_notes import LearningNoteRequest


def build_learning_note_prompt(payload: LearningNoteRequest) -> str:
    learned = "\n".join(f"- {item}" for item in payload.what_i_learned)
    questions = "\n".join(f"- {item}" for item in payload.questions)
    return (
        "Summarize the learning chapter into a concise study note.\n"
        f"Topic: {payload.topic}\n"
        f"Chapter: {payload.chapter_title}\n"
        f"Learned:\n{learned}\n"
        f"Questions:\n{questions}\n"
    )
