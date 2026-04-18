from pathlib import Path

from lumen_notes_platform.obsidian import ObsidianAdapter


def test_platform_service_can_list_tree_and_update_exact_path(tmp_path: Path):
    adapter = ObsidianAdapter(tmp_path)
    created = adapter.add("ES", "Modules", "original")

    tree = adapter.list()
    adapter.update(created.path, "updated")

    assert tree[0].path == "ES"
    assert tree[0].children[0].path == "ES/Modules.md"
    assert (tmp_path / "ES" / "Modules.md").read_text(encoding="utf-8") == "updated"
