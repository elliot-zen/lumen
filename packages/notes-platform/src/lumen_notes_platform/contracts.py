from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lumen_notes_platform.results import PlatformCommandResult


@dataclass(frozen=True)
class NoteTreeNode:
    name: str
    path: str
    node_type: str
    children: tuple["NoteTreeNode", ...] = ()


class NotesPlatformAdapter(Protocol):
    def list(self) -> list[NoteTreeNode]:
        """Return the current note tree."""

    def add(self, directory: str, title: str, content: str) -> PlatformCommandResult:
        """Create a note and return its path."""

    def update(self, path: str, content: str) -> PlatformCommandResult:
        """Replace the note content at the given exact path."""
