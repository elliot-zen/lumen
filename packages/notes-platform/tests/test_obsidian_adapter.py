from pathlib import Path
import subprocess

import pytest

from lumen_notes_platform.obsidian import ObsidianAdapter


def test_list_returns_tree_with_exact_paths(tmp_path: Path):
    (tmp_path / "ES").mkdir()
    (tmp_path / "ES" / "Promises.md").write_text("# Promises", encoding="utf-8")
    (tmp_path / "Python").mkdir()
    (tmp_path / "Python" / "Asyncio.md").write_text("# Asyncio", encoding="utf-8")

    adapter = ObsidianAdapter(tmp_path)
    tree = adapter.list()

    assert [node.path for node in tree] == ["ES", "Python"]
    assert tree[0].children[0].path == "ES/Promises.md"
    assert tree[1].children[0].path == "Python/Asyncio.md"


def test_update_replaces_existing_note_content(tmp_path: Path):
    adapter = ObsidianAdapter(tmp_path)
    result = adapter.add("ES", "Promises", "old")

    adapter.update(result.path, "new content")

    assert (tmp_path / result.path).read_text(encoding="utf-8") == "new content"


def test_update_rejects_missing_target(tmp_path: Path):
    adapter = ObsidianAdapter(tmp_path)

    with pytest.raises(FileNotFoundError):
        adapter.update("ES/Missing.md", "content")


def test_add_uses_obsidian_cli_when_configured(tmp_path: Path):
    calls: list[tuple[list[str], Path]] = []

    def fake_runner(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        calls.append((args, cwd))
        target = cwd / "ES" / "Promises.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("content", encoding="utf-8")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    adapter = ObsidianAdapter(
        tmp_path,
        vault_name="moon",
        cli_command="obsidian",
        runner=fake_runner,
    )

    result = adapter.add("ES", "Promises", "content")

    assert result.path == "ES/Promises.md"
    assert calls == [
        (
            [
                "obsidian",
                "vault=moon",
                "create",
                "path=ES/Promises.md",
                "content=content",
                "overwrite",
            ],
            tmp_path,
        )
    ]
    assert result.stdout == ""
    assert result.stderr == ""


def test_list_uses_cli_json_output_when_vault_name_is_configured(tmp_path: Path):
    def fake_runner(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        assert args == ["obsidian", "vault=moon", "files", "format=json"]
        assert cwd == tmp_path
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='["ES/Promises.md", "Python/Asyncio.md"]',
            stderr='warning noise',
        )

    adapter = ObsidianAdapter(
        tmp_path,
        vault_name="moon",
        cli_command="obsidian",
        runner=fake_runner,
    )

    tree = adapter.list()

    assert [node.path for node in tree] == ["ES", "Python"]
    assert tree[0].children[0].path == "ES/Promises.md"
