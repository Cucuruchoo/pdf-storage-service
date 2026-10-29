
import re
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from pymongo import AsyncMongoClient

from app.api.document_routes import (
    router as document_router,
)
from app.infrastructure.mongo_document_repository import (
    MongoDocumentRepository,
)
from app.infrastructure.request_logging import (
    configure_logger,
    request_id_context,
)
from app.infrastructure.settings import get_settings

logger = configure_logger()


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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    incoming_id = request.headers.get(
        "X-Request-ID",
        "",
    )

    if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", incoming_id):
        request_id = incoming_id
    else:
        request_id = uuid4().hex

    token = request_id_context.set(request_id)
    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code

        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as error:
        logger.error(
            "http_unhandled_error",
            extra={
                "request_id": request_id,
                "error_type": type(error).__name__,
            },
        )
        raise

    finally:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "http_request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )

        request_id_context.reset(token)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "pdf-storage-service",
    }
