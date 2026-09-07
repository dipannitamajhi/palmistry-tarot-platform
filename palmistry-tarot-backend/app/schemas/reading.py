from pydantic import BaseModel
from datetime import datetime
from typing import Any

from app.models.reading import ReadingType


class ReadingOut(BaseModel):
    id: int
    reading_type: ReadingType
    summary: str
    details: Any  # parsed JSON dict, built manually in the router (see users.py)
    created_at: datetime

    class Config:
        from_attributes = True
