from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Document:
    filename: str
    content_text: str
    checksum: str
    size_bytes: int
    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def character_count(self) -> int:
        return len(self.content_text)