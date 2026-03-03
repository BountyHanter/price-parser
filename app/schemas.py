from datetime import datetime
from pydantic import BaseModel


class ParseJobSchema(BaseModel):
    id: int
    site_name: str
    status: str

    total_items: int
    processed_items: int
    error_items: int

    started_at: datetime | None
    finished_at: datetime | None

    error_message: str | None

    class Config:
        from_attributes = True