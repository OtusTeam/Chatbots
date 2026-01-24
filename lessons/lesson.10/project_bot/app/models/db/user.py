from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from infra.db import Base


class UserDB(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # message.from_user.id
    tg_user_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )
    username: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    first_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    created_at: Mapped[str] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )
