
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from app.api.document_routes import router as document_router
from app.infrastructure.mongo_document_repository import MongoDocumentRepository
from app.infrastructure.settings import get_settings


async def initialize_indexes() -> None:
    settings = get_settings()

    async with AsyncMongoClient(settings.mongo_uri) as client:
        collection = client[settings.mongo_database][
            settings.mongo_collection
        ]

        repository = MongoDocumentRepository(collection)
        await repository.create_indexes()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_indexes()
    yield


app = FastAPI(
    title="PDF Storage Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(document_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "pdf-storage-service",
    }
