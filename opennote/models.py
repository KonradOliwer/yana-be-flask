import uuid
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from opennote.database import db


class Note(db.Model):
    __tablename__ = 'notes'
    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(unique=False, nullable=False)

    def __init__(self, id, name, content):
        self.id = id or uuid.uuid1()
        self.name = name
        self.content = content

