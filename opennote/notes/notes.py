import uuid
from typing import Optional, Literal

from flask import Blueprint, request, Response
from pydantic import BaseModel, Field
from sqlalchemy import desc

from common.error_handling import ClientError
from common.routing_decorators import json_serialization
from opennote.database import db
from opennote.db_model import Note

bluprint = Blueprint('notes', __name__, url_prefix='/notes')


class NotesClintError(ClientError[Literal[
    'NOTE_NOT_FOUND',
    'NOTE_ALREADY_EXISTS',
    'VALIDATION_ERROR'
]]):
    pass


class CreateNoteDTO(BaseModel):
    name: str = Field(..., max_length=50)
    content: Optional[str] = ""


class NoteDTO(CreateNoteDTO):
    id: uuid.UUID

    @classmethod
    def from_note(cls, note: Note) -> 'NoteDTO':
        return cls(id=note.id, name=note.name, content=note.content)


@bluprint.get('/')
@json_serialization
def get_all_notes() -> tuple[list[NoteDTO], int]:
    name = request.args.get('name')
    if name is not None:
        notes = db.session.query(Note).filter(Note.name == name).all()
        return [NoteDTO.from_note(note) for note in notes], 200

    notes = db.session.query(Note).order_by(desc(Note.updated_at)).all()
    return [NoteDTO.from_note(note) for note in notes], 200


@bluprint.put('/<uuid:id>')
@json_serialization
def update_note(id: uuid, body: NoteDTO) -> tuple[NoteDTO, int]:
    if id != body.id:
        raise NotesClintError(code="VALIDATION_ERROR", message="id: should match url id", status_code=400)
    note = db.session.query(Note).get(id)
    if note is None:
        raise NotesClintError(code="NOTE_NOT_FOUND", status_code=404)

    note.name = body.name
    note.content = body.content
    db.session.commit()
    return NoteDTO.from_note(note), 200


@bluprint.post('/')
@json_serialization
def create_note(body: CreateNoteDTO) -> tuple[NoteDTO, int]:
    note_in_db = db.session.query(Note).filter_by(name=body.name).first()
    if note_in_db:
        raise NotesClintError(code="NOTE_ALREADY_EXISTS", status_code=400)
    else:
        new_note = Note(
            id=uuid.uuid4(),
            name=body.name,
            content=body.content
        )
        db.session.add(new_note)
        db.session.commit()
        return NoteDTO.from_note(new_note), 201


@bluprint.delete('/<uuid:id>')
@json_serialization
def delete_note(id: uuid) -> tuple[Response, int]:
    note = db.session.query(Note).get(id)
    if note is None:
        raise NotesClintError(code="NOTE_NOT_FOUND", status_code=404)

    db.session.delete(note)
    db.session.commit()
    return Response(), 204