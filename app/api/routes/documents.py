
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.document import DocumentCreate, DocumentResponse
from app.database.connection import get_db
from app.services.document_service import (
    create_document,
    get_document_by_id,
    update_document,
    delete_document
)
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/", response_model=DocumentResponse, status_code=201)
def create_new_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db)
):
    document = create_document(
        db=db,
        filename=document_data.filename,
        file_path=document_data.file_path
    )

    return {
        "id": document.id,
        "filename": document.filename,
        "file_path": document.file_path,
        "created_at": document.created_at
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def read_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = get_document_by_id(
        db=db,
        document_id=document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "file_path": document.file_path,
        "created_at": document.created_at
    }


@router.put("/{document_id}", response_model=DocumentResponse)
def update_existing_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    document = update_document(
        db=db,
        document_id=document_id,
        new_filename=document_data.filename
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@router.delete("/{document_id}")
def delete_existing_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_document(
        db=db,
        document_id=document_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "message": "Document deleted successfully"
    }
