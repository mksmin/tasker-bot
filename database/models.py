# import from lib
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=True)


class User(TimeStampMixin, Base):
    __tablename__ = 'users'

    user_tg = mapped_column(BigInteger, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)

    tasks = relationship('Task', back_populates='user')
    settings = relationship('UserSettings', back_populates='user')


class Task(TimeStampMixin, Base):
    __tablename__ = 'tasks'

    text_task: Mapped[str] = mapped_column(String(500), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='tasks')

    def delete_task(self):
        self.is_done = True


class UserSettings(TimeStampMixin, Base):
    __tablename__ = 'user_settings'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    count_tasks: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    user = relationship('User', back_populates='settings')
