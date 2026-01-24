from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from infra.db import Base


class CareerProfileDB(Base):
    __tablename__ = 'career_profiles'
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
    profession: Mapped[str | None] = mapped_column(
        String,
        nullable=False,
    )
    grade: Mapped[str | None] = mapped_column(
        String,
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )
