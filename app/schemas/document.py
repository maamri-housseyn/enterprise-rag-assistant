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