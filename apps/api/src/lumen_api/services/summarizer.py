from __future__ import annotations

import httpx
from openai import OpenAI

from lumen_api.config import Settings, get_settings
from lumen_api.services.prompt_builder import build_learning_note_prompt
from lumen_domain.learning_notes import LearningNoteRequest


class Summarizer:
    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.Client | None = None,
        sdk_client_factory=OpenAI,
    ):
        self.settings = settings or get_settings()
        self.client = client
        self.sdk_client_factory = sdk_client_factory

    def summarize(self, payload: LearningNoteRequest) -> str:
        if self.settings.summarizer_base_url and self.settings.summarizer_api_key:
            return self._summarize_via_api(payload)
        return f"{payload.topic}: {payload.chapter_title} ({len(payload.what_i_learned)} key points)"

    def _summarize_via_api(self, payload: LearningNoteRequest) -> str:
        owns_client = self.client is None
        client = self.client or httpx.Client(
            timeout=self.settings.summarizer_timeout_seconds,
            verify=self._build_ssl_verify_config(),
        )
        try:
            sdk_client = self.sdk_client_factory(
                base_url=self.settings.summarizer_base_url,
                api_key=self.settings.summarizer_api_key,
                http_client=client,
            )
            response = sdk_client.chat.completions.create(
                model=self.settings.summarizer_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You summarize study notes into concise reusable knowledge.",
                    },
                    {
                        "role": "user",
                        "content": build_learning_note_prompt(payload),
                    },
                ],
            )
            return response.choices[0].message.content.strip()
        finally:
            if owns_client:
                client.close()

    def _build_ssl_verify_config(self) -> bool | str:
        if self.settings.summarizer_ca_bundle:
            return self.settings.summarizer_ca_bundle
        return self.settings.summarizer_verify_ssl
