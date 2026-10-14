from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreateRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    content_text: str = Field(..., min_length=1)
    checksum: str = Field(..., min_length=1)
    size_bytes: int = Field(..., ge=1)


class DocumentUpdateRequest(BaseModel):
    filename: str | None = Field(default=None, min_length=1)
    content_text: str | None = Field(default=None, min_length=1)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_text: str
    checksum: str
    character_count: int
    size_bytes: int
    created_at: datetime
    updated_at: datetime