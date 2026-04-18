from pathlib import Path

from lumen_api.config import get_settings


def test_get_settings_reads_values_from_dotenv(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "LUMEN_DATABASE_URL=postgresql+psycopg://dotenv:dotenv@localhost:5432/dotenv",
                "LUMEN_OBSIDIAN_VAULT_NAME=moon",
                "LUMEN_SUMMARIZER_MODEL=Qwen3.6-35B-A3B",
                "LUMEN_SUMMARIZER_VERIFY_SSL=false",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LUMEN_DATABASE_URL", raising=False)
    monkeypatch.delenv("LUMEN_OBSIDIAN_VAULT_NAME", raising=False)
    monkeypatch.delenv("LUMEN_SUMMARIZER_MODEL", raising=False)
    monkeypatch.delenv("LUMEN_SUMMARIZER_VERIFY_SSL", raising=False)

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://dotenv:dotenv@localhost:5432/dotenv"
    assert settings.obsidian_vault_name == "moon"
    assert settings.summarizer_model == "Qwen3.6-35B-A3B"
    assert settings.summarizer_verify_ssl is False
