# import from lib
from datetime import datetime, time, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=True,
    )


class User(TimeStampMixin, Base):
    __tablename__ = "users"

    user_tg = mapped_column(BigInteger, nullable=False, unique=True)
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    username: Mapped[str | None] = mapped_column(String(50))

    tasks = relationship(
        "Task",
        back_populates="user",
    )
    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
    )


class Task(TimeStampMixin, Base):
    __tablename__ = "tasks"

    text_task: Mapped[str] = mapped_column(String(500), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tasks")

    def delete_task(self) -> None:
        self.is_done = True


class UserSettings(TimeStampMixin, Base):
    __tablename__ = "user_settings"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    count_tasks: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    send_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        default=lambda: time(9, 0),
    )
    send_enable: Mapped[bool] = mapped_column(default=True, server_default="true")

    user = relationship("User", back_populates="settings", uselist=False)
