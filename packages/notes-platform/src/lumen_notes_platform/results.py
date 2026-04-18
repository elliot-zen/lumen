from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformCommandResult:
    path: str | None
    stdout: str
    stderr: str
