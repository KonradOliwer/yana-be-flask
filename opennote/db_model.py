import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from opennote.database import db


class Base(db.Model):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False)
    crated_at: Mapped[datetime] = mapped_column(server_default=func.CURRENT_TIMESTAMP())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, server_default=func.CURRENT_TIMESTAMP(),
                                                 onupdate=func.CURRENT_TIMESTAMP())


class Note(Base):
    __tablename__ = 'notes'
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(unique=False, nullable=False)

    def __init__(self, id, name, content):
        self.id = id or uuid.uuid1()
        self.name = name
        self.content = content


class User(Base):
    __tablename__ = 'users'
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(unique=False, nullable=False)
    password_salt: Mapped[str] = mapped_column(unique=True, nullable=False)


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    expire_at: Mapped[int] = mapped_column(nullable=False) # Unix timestamp
    active: Mapped[bool] = mapped_column(nullable=False, default=True)

    def __init__(self, user_id: UUID, expire_at: int, active: bool = True):
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.expire_at = expire_at
        self.active = active

