from app.domain.document import Document


def test_document_calculates_character_count():
    document = Document(
        filename="example.pdf",
        content_text="Extracted text",
        checksum="abc123",
        size_bytes=100,
    )

    assert document.character_count == 14