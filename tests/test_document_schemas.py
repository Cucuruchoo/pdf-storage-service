import pytest
from pydantic import ValidationError

from app.schemas.document_schema import DocumentCreateRequest, DocumentUpdateRequest


def test_document_create_request_accepts_valid_data():
    request = DocumentCreateRequest(
        filename="example.pdf",
        content_text="Extracted text",
        checksum="abc123",
        size_bytes=100,
    )

    assert request.filename == "example.pdf"
    assert request.content_text == "Extracted text"
    assert request.checksum == "abc123"
    assert request.size_bytes == 100


def test_document_create_request_rejects_empty_filename():
    with pytest.raises(ValidationError):
        DocumentCreateRequest(
            filename="",
            content_text="Extracted text",
            checksum="abc123",
            size_bytes=100,
        )


def test_document_create_request_rejects_invalid_size():
    with pytest.raises(ValidationError):
        DocumentCreateRequest(
            filename="example.pdf",
            content_text="Extracted text",
            checksum="abc123",
            size_bytes=0,
        )


def test_document_update_request_accepts_partial_data():
    request = DocumentUpdateRequest(filename="updated.pdf")

    assert request.filename == "updated.pdf"
    assert request.content_text is None