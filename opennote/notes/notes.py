import uuid
from enum import Enum
from typing import Optional

from flask import Blueprint, jsonify, request, Response
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.exc import IntegrityError

from opennote.database import db
from opennote.db_model import Note

notes_bluprint = Blueprint('notes', __name__, url_prefix='/notes')


class ErrorResponseCodes(Enum):
    NOT_FOUND = "NOTE_NOT_FOUND"
    WRITE_ERROR = "NOTE_WRITE_ERROR"
    VALIDATION_ERROR = "NOTE_VALIDATION_ERROR"


class ErrorResponse(BaseModel):
    message: str = None
    code: ErrorResponseCodes

    def to_dict(self):
        return {
            'code': self.code.value
        }


class CreateNoteDTO(BaseModel):
    name: str = Field(..., max_length=50)
    content: Optional[str] = ""


class NoteDTO(CreateNoteDTO):
    id: uuid.UUID

    @classmethod
    def from_note(cls, note: Note) -> 'NoteDTO':
        return cls(id=note.id, name=note.name, content=note.content)


@notes_bluprint.get('/')
def get_all_notes() -> tuple[Response, int]:
    name = request.args.get('name')
    if name:
        notes = db.session.query(Note).filter(Note.name == name).all()
        return jsonify([NoteDTO.from_note(note) for note in notes]), 200

    notes = db.session.query(Note).all()
    return jsonify([NoteDTO.from_note(note) for note in notes]), 200


@notes_bluprint.post('/')
def create_note() -> tuple[Response, int]:
    request_dto = CreateNoteDTO(**request.get_json())
    new_note = Note(
        id=uuid.uuid1(),
        name=request_dto.name,
        content=request_dto.content
    )
    note_in_db = db.session.query(Note).filter_by(name=new_note.name).first()
    if note_in_db:
        note_in_db.content = new_note.content
        db.session.commit()
        return jsonify(NoteDTO.from_note(note_in_db)), 200
    else:
        db.session.add(new_note)
        db.session.commit()
        return jsonify(NoteDTO.from_note(new_note)), 201


@notes_bluprint.get('/<uuid:id>')
def get_note(id: uuid) -> tuple[Response, int]:
    note = db.session.query(Note).get(id)
    if note is None:
        return jsonify({'error': 'Note not found'}), 404
    return jsonify(NoteDTO.from_note(note)), 200


@notes_bluprint.delete('/<uuid:id>')
def delete_note(id: uuid) -> tuple[Response, int]:
    note = db.session.query(Note).get(id)
    if note is None:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.NOT_FOUND)), 404

    db.session.delete(note)
    db.session.commit()
    return Response(), 204


@notes_bluprint.errorhandler(IntegrityError)
def handle_exception(e) -> tuple[Response, int]:
    return jsonify(ErrorResponse(code=ErrorResponseCodes.WRITE_ERROR)), 400


@notes_bluprint.errorhandler(ValidationError)
def handle(error):
    message = '\n'.join(f"{', '.join(e['loc'])}: {e['msg']}" for e in error.errors())
    return jsonify(ErrorResponse(code=ErrorResponseCodes.VALIDATION_ERROR), message=message), 400
