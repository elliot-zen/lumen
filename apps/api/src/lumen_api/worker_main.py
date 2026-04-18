from __future__ import annotations

import time

from lumen_api.config import get_settings
from lumen_api.db import SessionLocal, init_database
from lumen_api.services.worker import Worker
from lumen_api.services.summarizer import Summarizer
from lumen_notes_platform.obsidian import ObsidianAdapter


def run_worker_forever() -> None:
    settings = get_settings()
    init_database(settings)
    while True:
        with SessionLocal() as session:
            settings = get_settings()
            worker = Worker(
                session=session,
                notes_platform=ObsidianAdapter(
                    settings.obsidian_vault_root,
                    vault_name=settings.obsidian_vault_name,
                    cli_command=settings.obsidian_cli_command,
                ),
                summarizer=Summarizer(settings=settings),
            )
            worker.recover_stale_jobs(settings.stale_processing_seconds)
            processed = worker.process_next()
        if processed is None:
            time.sleep(settings.worker_poll_interval_seconds)


if __name__ == "__main__":
    run_worker_forever()
