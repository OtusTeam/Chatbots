from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from infra.db import Base


class MessageHistoryDB(Base):
    __tablename__ = 'message_history'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    tg_user_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )
    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )
