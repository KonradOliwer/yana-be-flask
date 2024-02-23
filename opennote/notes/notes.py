import uuid
from enum import Enum

from flask import Blueprint, jsonify, request, Response
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

from opennote.database import db
from opennote.db_model import Note

notes_bluprint = Blueprint('notes', __name__, url_prefix='/notes')


class ErrorResponseCodes(Enum):
    NOT_FOUND = "NOTE_NOT_FOUND"
    BLANK_NAME = "NOTE_WITH_BLANK_NAME"
    ALREADY_EXISTS = "NOTE_ALREADY_EXISTS"
    NOT_MATCHING_URL_ID = "NOTE_ID_NOT_MATCHING_URL_ID"
    WRITE_ERROR = "NOTE_WRITE_ERROR"


class ErrorResponse(BaseModel):
    code: ErrorResponseCodes

    def to_dict(self):
        return {
            'code': self.code.value
        }


class CreateNoteDTO(BaseModel):
    name: str = Field(..., max_length=50)
    content: str


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
    try:
        request_dto = CreateNoteDTO(**request.get_json())
        new_note = Note(
            id=uuid.uuid1(),
            name=request_dto.name,
            content=request_dto.content
        )
        db.session.add(new_note)
        db.session.commit()
        return jsonify(NoteDTO.from_note(new_note)), 201
    except IntegrityError:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.ALREADY_EXISTS)), 400


@notes_bluprint.get('/<uuid:id>')
def get_note(id: uuid) -> tuple[Response, int]:
    note = db.session.query(Note).get(id)
    if note is None:
        return jsonify({'error': 'Note not found'}), 404
    return jsonify(NoteDTO.from_note(note)), 200


@notes_bluprint.put('/<uuid:id>')
def edit_note(id: uuid) -> tuple[Response, int]:
    request_dto = NoteDTO(**request.get_json())
    if request_dto.id != id:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.NOT_MATCHING_URL_ID)), 400

    persisted_note = db.session.query(Note).get(id)
    if persisted_note is not None:
        if request_dto.name.strip() and request_dto.content.strip() != "":
            jsonify({'error': 'Note need to have not blank name'}), 400
        persisted_note.name = request_dto.name
        persisted_note.content = request_dto.content
        db.session.commit()
        return jsonify(NoteDTO.from_note(persisted_note)), 200
    else:
        return jsonify(ErrorResponse(code=ErrorResponseCodes.NOT_FOUND)), 404


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
