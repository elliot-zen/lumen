from types import SimpleNamespace

import httpx

from lumen_api.config import Settings
from lumen_api.services.summarizer import Summarizer
from lumen_domain.learning_notes import LearningNoteRequest


def test_summarizer_uses_openai_sdk_when_configured():
    captured: dict = {}

    def fake_create(**payload):
        captured["payload"] = payload
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Concise summary")
                )
            ]
        )

    def fake_factory(**kwargs):
        captured["kwargs"] = kwargs
        return SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=fake_create
                )
            )
        )

    settings = Settings(
        summarizer_base_url="http://testserver",
        summarizer_api_key="test",
    )
    summarizer = Summarizer(settings=settings, sdk_client_factory=fake_factory)

    summary = summarizer.summarize(
        LearningNoteRequest(
            type="learning_note",
            topic="ES",
            chapter_title="Async Iteration",
            what_i_learned=["for await...of iterates async values"],
            questions=["When should I use streams?"],
        )
    )

    assert summary == "Concise summary"
    assert captured["kwargs"]["base_url"] == "http://testserver"
    assert captured["kwargs"]["api_key"] == "test"
    assert captured["payload"]["model"] == settings.summarizer_model
    assert captured["payload"]["messages"][1]["content"].count("Async Iteration") == 1


def test_summarizer_can_disable_ssl_verification_for_self_signed_certificates(monkeypatch):
    captured: dict = {}

    def fake_httpx_client(**kwargs):
        captured["verify"] = kwargs["verify"]
        captured["timeout"] = kwargs["timeout"]
        return SimpleNamespace(close=lambda: None)

    def fake_factory(**kwargs):
        return SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **payload: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content="Concise summary")
                            )
                        ]
                    )
                )
            )
        )

    monkeypatch.setattr("lumen_api.services.summarizer.httpx.Client", fake_httpx_client)
    settings = Settings(
        summarizer_base_url="https://self-signed.test/v1",
        summarizer_api_key="test",
        summarizer_verify_ssl=False,
    )
    summarizer = Summarizer(settings=settings, sdk_client_factory=fake_factory)

    summary = summarizer.summarize(
        LearningNoteRequest(
            type="learning_note",
            topic="ES",
            chapter_title="Async Iteration",
            what_i_learned=["for await...of iterates async values"],
            questions=["When should I use streams?"],
        )
    )

    assert summary == "Concise summary"
    assert captured["verify"] is False
    assert captured["timeout"] == settings.summarizer_timeout_seconds
