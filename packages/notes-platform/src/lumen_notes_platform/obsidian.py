from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Protocol

from lumen_notes_platform.contracts import NoteTreeNode
from lumen_notes_platform.results import PlatformCommandResult


class CommandRunner(Protocol):
    def __call__(self, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]: ...


def _default_runner(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )


class ObsidianAdapter:
    def __init__(
        self,
        vault_root: str | Path,
        vault_name: str | None = None,
        cli_command: str | None = None,
        runner: CommandRunner | None = None,
    ):
        self.vault_root = Path(vault_root)
        self.vault_root.mkdir(parents=True, exist_ok=True)
        self.vault_name = vault_name
        self.cli_command = cli_command
        self.runner = runner or _default_runner

    def list(self) -> list[NoteTreeNode]:
        if self.cli_command and self.vault_name:
            completed = self.runner(
                self._build_cli_args("files", "format=json"),
                cwd=self.vault_root,
            )
            return self._tree_from_paths(self._parse_cli_paths(completed.stdout))
        return list(self._walk(self.vault_root, Path("")))

    def add(self, directory: str, title: str, content: str) -> PlatformCommandResult:
        safe_directory = directory.strip().replace("\\", "/")
        safe_title = title.strip()
        note_path = Path(safe_directory) / f"{safe_title}.md"
        return self._create_or_overwrite(note_path.as_posix(), content)

    def update(self, path: str, content: str) -> PlatformCommandResult:
        if self.cli_command and self.vault_name:
            available_paths = {node.path for node in self._flatten_tree(self.list())}
            if path not in available_paths:
                raise FileNotFoundError(f"Note path does not exist: {path}")
            return self._create_or_overwrite(path, content)

        note_path = self.vault_root / path
        if not note_path.exists():
            raise FileNotFoundError(f"Note path does not exist: {path}")
        if note_path.is_dir():
            raise IsADirectoryError(f"Expected a note file path, got directory: {path}")
        return self._create_or_overwrite(path, content)

    def _walk(self, current_path: Path, relative: Path) -> tuple[NoteTreeNode, ...]:
        nodes: list[NoteTreeNode] = []
        for child in sorted(current_path.iterdir(), key=lambda item: (item.is_file(), item.name.lower())):
            child_relative = relative / child.name
            if child.is_dir():
                nodes.append(
                    NoteTreeNode(
                        name=child.name,
                        path=child_relative.as_posix(),
                        node_type="folder",
                        children=self._walk(child, child_relative),
                    )
                )
            else:
                nodes.append(
                    NoteTreeNode(
                        name=child.name,
                        path=child_relative.as_posix(),
                        node_type="note",
                    )
                )
        return tuple(nodes)

    def _create_or_overwrite(self, path: str, content: str) -> PlatformCommandResult:
        if self.cli_command:
            completed = self.runner(
                self._build_cli_args(
                    "create",
                    f"path={path}",
                    f"content={content}",
                    "overwrite",
                ),
                cwd=self.vault_root,
            )
            return PlatformCommandResult(
                path=path,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )

        absolute_path = self.vault_root / path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text(content, encoding="utf-8")
        return PlatformCommandResult(path=path, stdout="", stderr="")

    def _build_cli_args(self, command: str, *args: str) -> list[str]:
        if self.cli_command is None:
            raise RuntimeError("CLI command is not configured")
        cli_args = [self.cli_command]
        if self.vault_name:
            cli_args.append(f"vault={self.vault_name}")
        cli_args.append(command)
        cli_args.extend(args)
        return cli_args

    def _parse_cli_paths(self, stdout: str) -> list[str]:
        try:
            data = json.loads(stdout or "[]")
        except json.JSONDecodeError:
            return self._parse_plaintext_paths(stdout)

        if isinstance(data, list):
            paths: list[str] = []
            for item in data:
                if isinstance(item, str):
                    paths.append(item)
                elif isinstance(item, dict) and "path" in item:
                    paths.append(str(item["path"]))
            return paths
        return self._parse_plaintext_paths(stdout)

    def _parse_plaintext_paths(self, stdout: str) -> list[str]:
        paths: list[str] = []
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("[") or line.startswith("Gtk-Message:") or line.startswith("error:"):
                continue
            if "/" in line or line.endswith(".md"):
                paths.append(line)
        return paths

    def _tree_from_paths(self, paths: list[str]) -> list[NoteTreeNode]:
        tree: dict[str, dict] = {}
        for path in sorted(paths):
            parts = path.split("/")
            cursor = tree
            built_parts: list[str] = []
            for index, part in enumerate(parts):
                built_parts.append(part)
                node = cursor.setdefault(
                    part,
                    {
                        "path": "/".join(built_parts),
                        "type": "note" if index == len(parts) - 1 else "folder",
                        "children": {},
                    },
                )
                if index != len(parts) - 1:
                    node["type"] = "folder"
                    cursor = node["children"]
        return [self._materialize_node(name, data) for name, data in tree.items()]

    def _materialize_node(self, name: str, data: dict) -> NoteTreeNode:
        children = tuple(
            self._materialize_node(child_name, child_data)
            for child_name, child_data in sorted(data["children"].items())
        )
        return NoteTreeNode(
            name=name,
            path=data["path"],
            node_type=data["type"],
            children=children,
        )

    def _flatten_tree(self, nodes: list[NoteTreeNode]) -> list[NoteTreeNode]:
        flattened: list[NoteTreeNode] = []
        for node in nodes:
            flattened.append(node)
            flattened.extend(self._flatten_tree(list(node.children)))
        return flattened
