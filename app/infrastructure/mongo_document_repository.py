from datetime import UTC, datetime

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.domain.document import Document
from app.domain.document_repository import DocumentRepository
from app.domain.exceptions import DuplicateDocumentError


class MongoDocumentRepository(DocumentRepository):
    def __init__(self, collection):
        self.collection = collection

    async def create_indexes(self) -> None:
        await self.collection.create_index("checksum", unique=True)

    async def create(self, document: Document) -> Document:
        now = datetime.now(UTC)

        document_data = {
            "filename": document.filename,
            "content_text": document.content_text,
            "checksum": document.checksum,
            "size_bytes": document.size_bytes,
            "created_at": now,
            "updated_at": now,
        }

        try:
            result = await self.collection.insert_one(document_data)
        except DuplicateKeyError as error:
            raise DuplicateDocumentError("Document already exists.") from error

        document_data["_id"] = result.inserted_id

        return self._to_domain(document_data)

    async def find_by_id(self, document_id: str) -> Document | None:
        if not ObjectId.is_valid(document_id):
            return None

        document_data = await self.collection.find_one({"_id": ObjectId(document_id)})

        if document_data is None:
            return None

        return self._to_domain(document_data)

    async def find_by_checksum(self, checksum: str) -> Document | None:
        document_data = await self.collection.find_one({"checksum": checksum})

        if document_data is None:
            return None

        return self._to_domain(document_data)

    async def list_all(self) -> list[Document]:
        documents: list[Document] = []

        cursor = self.collection.find().sort("created_at", -1)

        async for document_data in cursor:
            documents.append(self._to_domain(document_data))

        return documents

    async def update(
        self,
        document_id: str,
        filename: str | None = None,
        content_text: str | None = None,
    ) -> Document | None:
        if not ObjectId.is_valid(document_id):
            return None

        update_data = {
            "updated_at": datetime.now(UTC),
        }

        if filename is not None:
            update_data["filename"] = filename

        if content_text is not None:
            update_data["content_text"] = content_text

        document_data = await self.collection.find_one_and_update(
            {"_id": ObjectId(document_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )

        if document_data is None:
            return None

        return self._to_domain(document_data)

    async def delete(self, document_id: str) -> bool:
        if not ObjectId.is_valid(document_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(document_id)})

        return result.deleted_count == 1

    def _to_domain(self, document_data: dict) -> Document:
        return Document(
            id=str(document_data["_id"]),
            filename=document_data["filename"],
            content_text=document_data["content_text"],
            checksum=document_data["checksum"],
            size_bytes=document_data["size_bytes"],
            created_at=document_data["created_at"],
            updated_at=document_data["updated_at"],
        )