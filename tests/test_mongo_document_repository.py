from datetime import UTC, datetime

import pytest
from bson import ObjectId

from app.infrastructure.mongo_document_repository import MongoDocumentRepository


@pytest.mark.asyncio
async def test_find_by_id_returns_none_when_id_is_invalid():
    repository = MongoDocumentRepository(collection=None)

    document = await repository.find_by_id("invalid-id")

    assert document is None


def test_to_domain_maps_mongo_document_to_document():
    repository = MongoDocumentRepository(collection=None)
    document_id = ObjectId()
    created_at = datetime(2026, 1, 1, tzinfo=UTC)
    updated_at = datetime(2026, 1, 2, tzinfo=UTC)

    document = repository._to_domain(
        {
            "_id": document_id,
            "filename": "example.pdf",
            "content_text": "Extracted text",
            "checksum": "abc123",
            "size_bytes": 100,
            "created_at": created_at,
            "updated_at": updated_at,
        }
    )

    assert document.id == str(document_id)
    assert document.filename == "example.pdf"
    assert document.content_text == "Extracted text"
    assert document.checksum == "abc123"
    assert document.character_count == 14
    assert document.size_bytes == 100
    assert document.created_at == created_at
    assert document.updated_at == updated_at