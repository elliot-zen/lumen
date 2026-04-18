from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api/src"))
sys.path.insert(0, str(ROOT / "packages/domain/src"))
sys.path.insert(0, str(ROOT / "packages/notes-platform/src"))

from lumen_api.config import get_settings
from lumen_notes_platform.obsidian import ObsidianAdapter


def main() -> None:
    settings = get_settings()
    adapter = ObsidianAdapter(
        settings.obsidian_vault_root,
        vault_name=settings.obsidian_vault_name,
        cli_command=settings.obsidian_cli_command,
    )
    created = adapter.add("Lumen", "Smoke Test", "# Smoke Test\n\nCreated by lumen.")
    tree = adapter.list()
    updated = adapter.update(created.path, "# Smoke Test\n\nUpdated by lumen.")

    print("CREATED", created.path)
    print("LIST_TOP_LEVEL", [node.path for node in tree])
    print("ADD_STDERR", created.stderr)
    print("UPDATE_STDERR", updated.stderr)


if __name__ == "__main__":
    main()
