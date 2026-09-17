from __future__ import annotations

from pathlib import Path
from kif.core.models import UsageRecord


class UsageStore:
    """Append-only JSONL store. Sufficient for Gate Zero."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def record(self, usage: UsageRecord) -> None:
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(usage.model_dump_json() + "\n")

    def all(self) -> list[UsageRecord]:
        if not self._path.exists():
            return []
        return [
            UsageRecord.model_validate_json(line)
            for line in self._path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
