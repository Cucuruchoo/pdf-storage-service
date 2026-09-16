from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_document_service
from app.domain.document import Document
from app.domain.exceptions import DocumentNotFoundError, DuplicateDocumentError
from app.main import app


class FakeDocumentService:
    def __init__(self):
        self.document = Document(
            id="doc-1",
            filename="example.pdf",
            content_text="Extracted text",
            checksum="abc123",
            size_bytes=100,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        self.should_raise_duplicate = False
        self.should_raise_not_found = False

    async def create_document(
        self,
        filename: str,
        content_text: str,
        checksum: str,
        size_bytes: int,
    ) -> Document:
        if self.should_raise_duplicate:
            raise DuplicateDocumentError("Document already exists.")

        return Document(
            id="doc-1",
            filename=filename,
            content_text=content_text,
            checksum=checksum,
            size_bytes=size_bytes,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    async def list_documents(self) -> list[Document]:
        return [self.document]

    async def get_document(self, document_id: str) -> Document:
        if self.should_raise_not_found:
            raise DocumentNotFoundError("Document not found.")

        return self.document

    async def update_document(
        self,
        document_id: str,
        filename: str | None = None,
        content_text: str | None = None,
    ) -> Document:
        if filename is None and content_text is None:
            raise ValueError("At least one field must be provided.")

        if self.should_raise_not_found:
            raise DocumentNotFoundError("Document not found.")

        return Document(
            id=document_id,
            filename=filename or self.document.filename,
            content_text=content_text or self.document.content_text,
            checksum=self.document.checksum,
            size_bytes=self.document.size_bytes,
            created_at=self.document.created_at,
            updated_at=datetime(2026, 1, 2, tzinfo=UTC),
        )

    async def delete_document(self, document_id: str) -> None:
        if self.should_raise_not_found:
            raise DocumentNotFoundError("Document not found.")


@pytest.fixture
def fake_service():
    return FakeDocumentService()


@pytest.fixture
def client(fake_service):
    app.dependency_overrides[get_document_service] = lambda: fake_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_document_returns_created_document(client):
    response = client.post(
        "/internal/v1/documents",
        json={
            "filename": "example.pdf",
            "content_text": "Extracted text",
            "checksum": "abc123",
            "size_bytes": 100,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == "doc-1"
    assert response.json()["filename"] == "example.pdf"
    assert response.json()["character_count"] == 14


def test_create_document_returns_conflict_when_checksum_exists(
    client,
    fake_service,
):
    fake_service.should_raise_duplicate = True

    response = client.post(
        "/internal/v1/documents",
        json={
            "filename": "example.pdf",
            "content_text": "Extracted text",
            "checksum": "abc123",
            "size_bytes": 100,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Document already exists."


def test_list_documents_returns_documents(client):
    response = client.get("/internal/v1/documents")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "doc-1"


def test_get_document_returns_document(client):
    response = client.get("/internal/v1/documents/doc-1")

    assert response.status_code == 200
    assert response.json()["id"] == "doc-1"


def test_get_document_returns_not_found(client, fake_service):
    fake_service.should_raise_not_found = True

    response = client.get("/internal/v1/documents/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_update_document_returns_updated_document(client):
    response = client.patch(
        "/internal/v1/documents/doc-1",
        json={
            "filename": "updated.pdf",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == "doc-1"
    assert response.json()["filename"] == "updated.pdf"


def test_update_document_rejects_empty_body(client):
    response = client.patch(
        "/internal/v1/documents/doc-1",
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "At least one field must be provided."


def test_delete_document_returns_no_content(client):
    response = client.delete("/internal/v1/documents/doc-1")

    assert response.status_code == 204
    assert response.content == b""