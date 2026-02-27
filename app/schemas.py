from pydantic import BaseModel
from datetime import datetime


class ParseJobStatus(BaseModel):
    id: int
    status: str

    total_items: int
    processed_items: int
    progress_percent: float

    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None

    class Config:
        from_attributes = True