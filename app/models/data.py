from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, DateTime, Text, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ParseStatus(str, Enum):
    pending = "pending"
    running = "running"
    finished = "finished"
    created = "created"
    failed = "failed"


class ParseJob(Base):
    __tablename__ = "parse_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    site_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[ParseStatus] = mapped_column(
        SQLEnum(ParseStatus),
        default=ParseStatus.pending,
        nullable=False,
    )

    total_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    processed_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )