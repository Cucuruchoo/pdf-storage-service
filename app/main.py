from fastapi import FastAPI

from app.api.document_routes import router as document_router

app = FastAPI(
    title="PDF Storage Service",
    version="0.1.0",
)

app.include_router(document_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "pdf-storage-service",
    }