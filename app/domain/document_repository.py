from abc import ABC, abstractmethod

from app.domain.document import Document


class DocumentRepository(ABC):
    @abstractmethod
    async def create(self, document: Document) -> Document:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, document_id: str) -> Document | None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_checksum(self, checksum: str) -> Document | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        document_id: str,
        filename: str | None = None,
        content_text: str | None = None,
    ) -> Document | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        raise NotImplementedError