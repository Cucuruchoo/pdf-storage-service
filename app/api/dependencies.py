from pymongo import AsyncMongoClient

from app.application.document_service import DocumentService
from app.infrastructure.mongo_document_repository import MongoDocumentRepository
from app.infrastructure.settings import get_settings

_mongo_client: AsyncMongoClient | None = None


def get_mongo_client() -> AsyncMongoClient:
    global _mongo_client

    if _mongo_client is None:
        settings = get_settings()
        _mongo_client = AsyncMongoClient(settings.mongo_uri)

    return _mongo_client


def get_document_service() -> DocumentService:
    settings = get_settings()
    client = get_mongo_client()
    database = client[settings.mongo_database]
    collection = database[settings.mongo_collection]
    repository = MongoDocumentRepository(collection=collection)

    return DocumentService(repository=repository)