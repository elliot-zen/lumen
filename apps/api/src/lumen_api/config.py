import os
from pathlib import Path

from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Settings(BaseModel):
    database_url: str = Field(
        default="postgresql+psycopg://lumen:lumen@localhost:5432/lumen"
    )
    worker_poll_interval_seconds: float = 2.0
    stale_processing_seconds: int = 300
    notes_platform: str = "obsidian"
    obsidian_vault_root: Path = Path("./tmp/obsidian-vault")
    obsidian_vault_name: str | None = None
    obsidian_cli_command: str = "obsidian"
    summarizer_model: str = "gpt-4.1-mini"
    summarizer_base_url: str | None = None
    summarizer_api_key: str | None = None
    summarizer_timeout_seconds: float = 30.0
    summarizer_verify_ssl: bool = True
    summarizer_ca_bundle: str | None = None


def get_settings() -> Settings:
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    return Settings(
        database_url=os.getenv(
            "LUMEN_DATABASE_URL",
            "postgresql+psycopg://lumen:lumen@localhost:5432/lumen",
        ),
        worker_poll_interval_seconds=float(os.getenv("LUMEN_WORKER_POLL_INTERVAL_SECONDS", "2.0")),
        stale_processing_seconds=int(os.getenv("LUMEN_STALE_PROCESSING_SECONDS", "300")),
        notes_platform=os.getenv("LUMEN_NOTES_PLATFORM", "obsidian"),
        obsidian_vault_root=Path(os.getenv("LUMEN_OBSIDIAN_VAULT_ROOT", "./tmp/obsidian-vault")),
        obsidian_vault_name=os.getenv("LUMEN_OBSIDIAN_VAULT_NAME"),
        obsidian_cli_command=os.getenv("LUMEN_OBSIDIAN_CLI_COMMAND", "obsidian"),
        summarizer_model=os.getenv("LUMEN_SUMMARIZER_MODEL", "gpt-4.1-mini"),
        summarizer_base_url=os.getenv("LUMEN_SUMMARIZER_BASE_URL"),
        summarizer_api_key=os.getenv("LUMEN_SUMMARIZER_API_KEY"),
        summarizer_timeout_seconds=float(os.getenv("LUMEN_SUMMARIZER_TIMEOUT_SECONDS", "30.0")),
        summarizer_verify_ssl=os.getenv("LUMEN_SUMMARIZER_VERIFY_SSL", "true").lower() in {"1", "true", "yes", "on"},
        summarizer_ca_bundle=os.getenv("LUMEN_SUMMARIZER_CA_BUNDLE"),
    )
