from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.models import Document, DocumentChunk
from app.database.connection import get_db
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
    delete_document
)
from app.generation.llm import generate_answer
from app.retrieval.search import search_similar_chunks


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
