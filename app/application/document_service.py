from app.domain.document import Document
from app.domain.document_repository import DocumentRepository
from app.domain.exceptions import DocumentNotFoundError, DuplicateDocumentError


class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    async def create_document(
        self,
        filename: str,
        content_text: str,
        checksum: str,
        size_bytes: int,
    ) -> Document:
        existing_document = await self.repository.find_by_checksum(checksum)

        if existing_document is not None:
            raise DuplicateDocumentError("Document already exists.")

        document = Document(
            filename=filename,
            content_text=content_text,
            checksum=checksum,
            size_bytes=size_bytes,
        )

        return await self.repository.create(document)

    async def get_document(self, document_id: str) -> Document:
        document = await self.repository.find_by_id(document_id)

        if document is None:
            raise DocumentNotFoundError("Document not found.")

        return document

    async def list_documents(self) -> list[Document]:
        return await self.repository.list_all()

    async def update_document(
        self,
        document_id: str,
        filename: str | None = None,
        content_text: str | None = None,
    ) -> Document:
        if filename is None and content_text is None:
            raise ValueError("At least one field must be provided.")

        document = await self.repository.update(
            document_id=document_id,
            filename=filename,
            content_text=content_text,
        )

        if document is None:
            raise DocumentNotFoundError("Document not found.")

        return document

    async def delete_document(self, document_id: str) -> None:
        deleted = await self.repository.delete(document_id)

        if not deleted:
            raise DocumentNotFoundError("Document not found.")