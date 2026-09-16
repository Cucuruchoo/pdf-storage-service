from datetime import UTC, datetime

import pytest

from app.application.document_service import DocumentService
from app.domain.document import Document
from app.domain.exceptions import DocumentNotFoundError, DuplicateDocumentError


class FakeDocumentRepository:
    def __init__(self):
        self.documents: dict[str, Document] = {}
        self.next_id = 1

    async def create(self, document: Document) -> Document:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        document_id = f"doc-{self.next_id}"
        self.next_id += 1

        saved_document = Document(
            id=document_id,
            filename=document.filename,
            content_text=document.content_text,
            checksum=document.checksum,
            size_bytes=document.size_bytes,
            created_at=now,
            updated_at=now,
        )

        self.documents[document_id] = saved_document
        return saved_document

    async def find_by_id(self, document_id: str) -> Document | None:
        return self.documents.get(document_id)

    async def find_by_checksum(self, checksum: str) -> Document | None:
        for document in self.documents.values():
            if document.checksum == checksum:
                return document

        return None

    async def list_all(self) -> list[Document]:
        return list(self.documents.values())

    async def update(
        self,
        document_id: str,
        filename: str | None = None,
        content_text: str | None = None,
    ) -> Document | None:
        document = self.documents.get(document_id)

        if document is None:
            return None

        updated_document = Document(
            id=document.id,
            filename=filename or document.filename,
            content_text=content_text or document.content_text,
            checksum=document.checksum,
            size_bytes=document.size_bytes,
            created_at=document.created_at,
            updated_at=datetime(2026, 1, 2, tzinfo=UTC),
        )

        self.documents[document_id] = updated_document
        return updated_document

    async def delete(self, document_id: str) -> bool:
        if document_id not in self.documents:
            return False

        del self.documents[document_id]
        return True


@pytest.mark.asyncio
async def test_create_document_when_checksum_is_unique():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    document = await service.create_document(
        filename="example.pdf",
        content_text="Extracted text",
        checksum="abc123",
        size_bytes=100,
    )

    assert document.id == "doc-1"
    assert document.filename == "example.pdf"
    assert document.checksum == "abc123"


@pytest.mark.asyncio
async def test_create_document_rejects_duplicate_checksum():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    await service.create_document(
        filename="example.pdf",
        content_text="Extracted text",
        checksum="abc123",
        size_bytes=100,
    )

    with pytest.raises(DuplicateDocumentError):
        await service.create_document(
            filename="copy.pdf",
            content_text="Extracted text",
            checksum="abc123",
            size_bytes=100,
        )


@pytest.mark.asyncio
async def test_get_document_returns_existing_document():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    created_document = await service.create_document(
        filename="example.pdf",
        content_text="Extracted text",
        checksum="abc123",
        size_bytes=100,
    )

    document = await service.get_document(created_document.id)

    assert document.id == created_document.id
    assert document.filename == "example.pdf"


@pytest.mark.asyncio
async def test_get_document_raises_error_when_document_does_not_exist():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    with pytest.raises(DocumentNotFoundError):
        await service.get_document("missing-id")


@pytest.mark.asyncio
async def test_list_documents_returns_all_documents():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    await service.create_document(
        filename="first.pdf",
        content_text="First text",
        checksum="abc123",
        size_bytes=100,
    )
    await service.create_document(
        filename="second.pdf",
        content_text="Second text",
        checksum="def456",
        size_bytes=200,
    )

    documents = await service.list_documents()

    assert len(documents) == 2


@pytest.mark.asyncio
async def test_update_document_changes_allowed_fields():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    created_document = await service.create_document(
        filename="example.pdf",
        content_text="Extracted text",
        checksum="abc123",
        size_bytes=100,
    )

    updated_document = await service.update_document(
        document_id=created_document.id,
        filename="updated.pdf",
    )

    assert updated_document.filename == "updated.pdf"
    assert updated_document.content_text == "Extracted text"
    assert updated_document.checksum == "abc123"


@pytest.mark.asyncio
async def test_update_document_requires_at_least_one_field():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    with pytest.raises(ValueError):
        await service.update_document(document_id="doc-1")


@pytest.mark.asyncio
async def test_delete_document_removes_existing_document():
    repository = FakeDocumentRepository()
    service = DocumentService(repository)

    created_document = await service.create_document(
        filename="example.pdf",
        content_text="Extracted text",
        checksum="abc123",
        size_bytes=100,
    )

    await service.delete_document(created_document.id)

    with pytest.raises(DocumentNotFoundError):
        await service.get_document(created_document.id)