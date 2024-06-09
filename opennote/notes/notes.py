import uuid
from enum import Enum
from typing import Optional

from flask import Blueprint, jsonify, request, Response
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from opennote.database import db
from opennote.db_model import Note

notes_bluprint = Blueprint('notes', __name__, url_prefix='/notes')


class ErrorResponseCodes(Enum):
    NOT_FOUND = "NOTE_NOT_FOUND"
    ALREADY_EXISTS = "NOTE_ALREADY_EXISTS"
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
    if name is not None:
        notes = db.session.query(Note).filter(Note.name == name).all()
        return jsonify([NoteDTO.from_note(note) for note in notes]), 200

    notes = db.session.query(Note).order_by(desc(Note.updated_at)).all()
    return jsonify([NoteDTO.from_note(note) for note in notes]), 200


@notes_bluprint.put('/<uuid:note_id>')
def update_note(note_id: uuid) -> tuple[Response, int]:
    request_dto = NoteDTO(**request.get_json())
    if note_id != request_dto.id:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.VALIDATION_ERROR, message="id: should match url id")), 400
    note = db.session.query(Note).get(note_id)
    if note is None:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.NOT_FOUND)), 404

    note.name = request_dto.name
    note.content = request_dto.content
    db.session.commit()
    return jsonify(NoteDTO.from_note(note)), 200


@notes_bluprint.post('/')
def create_note() -> tuple[Response, int]:
    request_dto = CreateNoteDTO(**request.get_json())
    note_in_db = db.session.query(Note).filter_by(name=request_dto.name).first()
    if note_in_db:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.ALREADY_EXISTS)), 400
    else:
        new_note = Note(
            id=uuid.uuid1(),
            name=request_dto.name,
            content=request_dto.content
        )
        db.session.add(new_note)
        db.session.commit()
        return jsonify(NoteDTO.from_note(new_note)), 201


@notes_bluprint.delete('/<uuid:note_id>')
def delete_note(note_id: uuid) -> tuple[Response, int]:
    note = db.session.query(Note).get(note_id)
    if note is None:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.NOT_FOUND)), 404

    db.session.delete(note)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.WRITE_ERROR)), 400
    return Response(), 204


@notes_bluprint.errorhandler(ValidationError)
def handle(error) -> tuple[Response, int]:
    message = '\n'.join(f"{', '.join(e['loc'])}: {e['msg']}" for e in error.errors())
    return jsonify(ErrorResponse(code=ErrorResponseCodes.VALIDATION_ERROR, message=message)), 400


@notes_bluprint.errorhandler(IntegrityError)
def handle_exception(e) -> tuple[Response, int]:
    return jsonify(ErrorResponse(code=ErrorResponseCodes.WRITE_ERROR)), 400
