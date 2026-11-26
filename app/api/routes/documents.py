from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import uuid

from app.database.models import Document, DocumentChunk
from app.database.connection import get_db
from app.core.config import UPLOAD_DIR
from app.ingestion.pdf_extractor import extract_pages_from_pdf
from app.ingestion.text_chunker import chunk_pages
from app.ingestion.embeddings import generate_embeddings

from app.generation.llm import generate_answer
from app.retrieval.search import search_similar_chunks
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    SearchResult,
    QuestionRequest,
    QuestionResponse,
    DocumentSource,
    MultiDocumentSearchResult,
    MultiDocumentQuestionResponse
)

from app.services.document_service import (
    create_document,
    get_document_by_id,
    update_document,
    delete_document,
    create_document_chunks,
    replace_document_chunks
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

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file extension
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # Read and validate file size
    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB."
        )

    # Generate a unique filename
    original_filename = Path(file.filename).name
    stored_filename = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / stored_filename

    document = None

    try:
        # Save the uploaded file
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(file_content)

        # Extract text from PDF pages
        pages = extract_pages_from_pdf(str(file_path))

        if not any(page["content"].strip() for page in pages):
            raise HTTPException(
                status_code=400,
                detail="The PDF does not contain extractable text."
            )

        # Split pages into chunks
        chunks = chunk_pages(
            pages=pages,
            chunk_size=100,
            overlap=20
        )

        # Generate embeddings
        embeddings = generate_embeddings(
            [chunk["content"] for chunk in chunks]
        )

        # Save document metadata
        document = create_document(
            db=db,
            filename=original_filename,
            file_path=str(file_path)
        )

        # Save document chunks and embeddings
        create_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            "id": document.id,
            "filename": document.filename,
            "file_path": document.file_path,
            "created_at": document.created_at
        }

    except HTTPException:
        if document is not None:
            delete_document(db=db, document_id=document.id)
        file_path.unlink(missing_ok=True)
        raise

    except Exception as error:
        if document is not None:
            delete_document(db=db, document_id=document.id)
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the PDF."
        ) from error
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


@router.post(
    "/{document_id}/replace",
    response_model=DocumentResponse
)
async def replace_existing_document(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check whether the document exists
    document = get_document_by_id(
        db=db,
        document_id=document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Validate the uploaded file
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB."
        )

    # Generate a unique filename
    original_filename = Path(file.filename).name
    stored_filename = f"{uuid.uuid4()}.pdf"
    new_file_path = UPLOAD_DIR / stored_filename

    old_file_path = Path(document.file_path)

    try:
        # Save the new PDF
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        new_file_path.write_bytes(file_content)

        # Extract text from the new PDF
        pages = extract_pages_from_pdf(str(new_file_path))

        if not any(page["content"].strip() for page in pages):
            raise HTTPException(
                status_code=400,
                detail="The PDF does not contain extractable text."
            )

        # Create new chunks
        chunks = chunk_pages(
            pages=pages,
            chunk_size=100,
            overlap=20
        )

        # Generate new embeddings
        embeddings = generate_embeddings(
            [chunk["content"] for chunk in chunks]
        )

        # Update document information and replace its chunks
        updated_document = replace_document_chunks(
            db=db,
            document_id=document_id,
            new_filename=original_filename,
            new_file_path=str(new_file_path),
            chunks=chunks,
            embeddings=embeddings
        )

        if updated_document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

    except HTTPException:
        new_file_path.unlink(missing_ok=True)
        raise

    except Exception as error:
        new_file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while replacing the PDF."
        ) from error

    # Delete the old PDF after the database update succeeds
    old_file_path.unlink(missing_ok=True)

    return updated_document


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
    # Retrieve the document before deleting its database record
    document = get_document_by_id(db, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Keep the file path before deleting the document
    file_path = Path(document.file_path)

    # Delete the document and its associated chunks
    deleted = delete_document(
        db=db,
        document_id=document_id
    )

    if deleted:
        # Delete the physical PDF file
        file_path.unlink(missing_ok=True)

    return {
        "message": "Document deleted successfully"
    }

@router.post("/{document_id}/search", response_model=SearchResult)
def search_document(
    document_id: int,
    question: str,
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

    results = search_similar_chunks(
        db=db,
        question=question,
        document_id=document_id,
        limit=3
    )

    formatted_results = [
        {
            "content": result[0].content,
            "distance": result.distance
        }
        for result in results
    ]

    return {
        "document_id": document_id,
        "question": question,
        "results": formatted_results
    }


@router.post("/{document_id}/ask", response_model=QuestionResponse)
def ask_document(
    document_id: int,
    question_data: QuestionRequest,
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

    # 1. Search for relevant chunks
    results = search_similar_chunks(
        db=db,
        question=question_data.question,
        document_id=document_id,
        limit=3
    )
    # 2. Handle cases where no relevant chunks are found
    if not results:
        return {
            "document_id": document_id,
            "question": question_data.question,
            "answer": "The document does not contain enough relevant information to answer this question.",
            "sources": []
        }
    # 3. Build the context
    context = "\n\n".join(
        f"[Page {result[0].page_number}]\n{result[0].content}"
        for result in results
    )

    # 4. Generate the answer
    answer = generate_answer(
        question=question_data.question,
        context=context
    )

    # 5. Format the sources
    sources = [
        {
            "page_number": result[0].page_number,
            "content": result[0].content,
            "distance": result.distance
        }
        for result in results
    ]

    return {
        "document_id": document_id,
        "question": question_data.question,
        "answer": answer,
        "sources": sources
    }



@router.post("/search", response_model=MultiDocumentSearchResult)
def search_all_documents(
    question_data: QuestionRequest,
    db: Session = Depends(get_db)
):
    results = search_similar_chunks(
        db=db,
        question=question_data.question,
        document_id=None,
        limit=5
    )

    formatted_results = []

    for chunk, distance in results:
        document = get_document_by_id(
            db=db,
            document_id=chunk.document_id
        )

        if document is None:
            continue

        formatted_results.append({
            "document_id": document.id,
            "filename": document.filename,
            "page_number": chunk.page_number,
            "content": chunk.content,
            "distance": float(distance)
        })

    return {
        "question": question_data.question,
        "results": formatted_results
    }



@router.post(
    "/ask",
    response_model=MultiDocumentQuestionResponse
)
def ask_all_documents(
    question_data: QuestionRequest,
    db: Session = Depends(get_db)
):
    # 1. Search across all documents
    results = search_similar_chunks(
        db=db,
        question=question_data.question,
        document_id=None,
        limit=5
    )

    # 2. Handle cases where no relevant chunks are found
    if not results:
        return {
            "question": question_data.question,
            "answer": (
                "The available documents do not contain "
                "enough relevant information to answer this question."
            ),
            "sources": []
        }

    # 3. Build sources and context
    sources = []
    context_parts = []

    for chunk, distance in results:
        document = get_document_by_id(
            db=db,
            document_id=chunk.document_id
        )

        if document is None:
            continue

        sources.append({
            "document_id": document.id,
            "filename": document.filename,
            "page_number": chunk.page_number,
            "content": chunk.content,
            "distance": float(distance)
        })

        context_parts.append(
            f"[Document: {document.filename} | "
            f"Page: {chunk.page_number}]\n{chunk.content}"
        )

    # 4. Handle cases where no valid sources remain
    if not sources:
        return {
            "question": question_data.question,
            "answer": (
                "The available documents do not contain "
                "enough relevant information to answer this question."
            ),
            "sources": []
        }

    context = "\n\n".join(context_parts)

    # 5. Generate the answer with the LLM
    answer = generate_answer(
        question=question_data.question,
        context=context
    )

    # 6. Return the answer and its sources
    return {
        "question": question_data.question,
        "answer": answer,
        "sources": sources
    }
