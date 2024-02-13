import uuid

from sqlalchemy import Column, Uuid, Text, String

from opennote.db import Base


class Note(Base):
    __tablename__ = 'notes'
    id = Column(Uuid, primary_key=True)
    name = Column(String(50), unique=False, nullable=False)
    content = Column(Text(), unique=False, nullable=False)

    def __init__(self, entity_id=uuid.uuid1(), name=None, content=None):
        self.id = entity_id
        self.name = name
        self.content = content

    def __repr__(self):
        return f'<Note {self.name!r} with id {self.id!r}>'
