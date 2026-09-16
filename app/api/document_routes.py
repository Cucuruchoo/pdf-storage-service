from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import get_document_service
from app.application.document_service import DocumentService
from app.domain.document import Document
from app.domain.exceptions import DocumentNotFoundError, DuplicateDocumentError
from app.schemas.document_schema import (
    DocumentCreateRequest,
    DocumentResponse,
    DocumentUpdateRequest,
)

router = APIRouter(prefix="/internal/v1/documents", tags=["documents"])

DocumentServiceDependency = Annotated[
    DocumentService,
    Depends(get_document_service),
]


def document_to_response(document: Document) -> DocumentResponse:
    if document.id is None:
        raise ValueError("Persisted document does not have id.")

    if document.created_at is None:
        raise ValueError("Persisted document does not have created_at.")

    if document.updated_at is None:
        raise ValueError("Persisted document does not have updated_at.")

    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        content_text=document.content_text,
        checksum=document.checksum,
        character_count=document.character_count,
        size_bytes=document.size_bytes,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    request: DocumentCreateRequest,
    service: DocumentServiceDependency,
) -> DocumentResponse:
    try:
        document = await service.create_document(
            filename=request.filename,
            content_text=request.content_text,
            checksum=request.checksum,
            size_bytes=request.size_bytes,
        )
    except DuplicateDocumentError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return document_to_response(document)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    service: DocumentServiceDependency,
) -> list[DocumentResponse]:
    documents = await service.list_documents()

    return [document_to_response(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    service: DocumentServiceDependency,
) -> DocumentResponse:
    try:
        document = await service.get_document(document_id)
    except DocumentNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return document_to_response(document)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    service: DocumentServiceDependency,
) -> DocumentResponse:
    try:
        document = await service.update_document(
            document_id=document_id,
            filename=request.filename,
            content_text=request.content_text,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except DocumentNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return document_to_response(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    service: DocumentServiceDependency,
) -> Response:
    try:
        await service.delete_document(document_id)
    except DocumentNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)