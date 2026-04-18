from lumen_domain.learning_notes import LearningNoteRequest, build_dedupe_key


def test_build_dedupe_key_is_stable_for_normalized_payload():
    first = LearningNoteRequest(
        type="learning_note",
        topic=" ES ",
        chapter_title="Promise",
        what_i_learned=["A", "B"],
        questions=["Q1"],
    )
    second = LearningNoteRequest(
        type="learning_note",
        topic="es",
        chapter_title="promise",
        what_i_learned=["A", "B"],
        questions=["Q1"],
    )

    assert build_dedupe_key(first) == build_dedupe_key(second)


def test_learning_note_request_rejects_blank_items():
    try:
        LearningNoteRequest(
            type="learning_note",
            topic="ES",
            chapter_title="Promise",
            what_i_learned=["valid", "   "],
            questions=["Q1"],
        )
    except Exception as exc:
        assert "non-blank" in str(exc)
    else:  # pragma: no cover - red path assertion
        raise AssertionError("Expected validation failure")
