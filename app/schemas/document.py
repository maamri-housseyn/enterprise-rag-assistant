from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    filename: str
    file_path: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentUpdate(BaseModel):
    filename: str

class SearchResult(BaseModel):
    document_id: int
    question: str
    results: list[dict]    

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    document_id: int
    question: str
    answer: str
    sources: list[dict]



class DocumentSource(BaseModel):
    document_id: int
    filename: str
    page_number: int
    content: str
    distance: float


class MultiDocumentSearchResult(BaseModel):
    question: str
    results: list[DocumentSource]


class MultiDocumentQuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[DocumentSource]
