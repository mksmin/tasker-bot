# import from lib
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

# import from modules
from database import Base, TimeStampMixin


class User(TimeStampMixin, Base):
    __tablename__ = 'users'

    user_tg = mapped_column(BigInteger, nullable=False, unique=True)

    tasks = relationship('Task', back_populates='user')

class Task(TimeStampMixin, Base):
    __tablename__ = 'tasks'

    text_task: Mapped[str] = mapped_column(String(255), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='tasks')