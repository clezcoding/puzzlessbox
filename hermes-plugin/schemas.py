import uuid

from pydantic import BaseModel


class DraftPreview(BaseModel):
    id: uuid.UUID
    title: str
    type: str
    category: str
    summary: str
