import uuid

from flask import Blueprint, jsonify, request, Response
from pydantic import BaseModel, Field

from opennote.database import db
from opennote.models import Note

notes_bluprint = Blueprint('notes', __name__, url_prefix='/notes')


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
    return jsonify([NoteDTO.from_note(note).__dict__ for note in db.session.query(Note).all()]), 200


@notes_bluprint.post('/')
def create_note() -> tuple[Response, int]:
    request_dto = CreateNoteDTO(**request.get_json())
    new_note = Note(
        id=uuid.uuid1(),
        name=request_dto.name,
        content=request_dto.content
    )
    db.session.add(new_note)
    db.session.commit()
    return jsonify(NoteDTO.from_note(new_note).__dict__), 201


@notes_bluprint.get('/<uuid:id>')
def get_note(id: uuid) -> tuple[Response, int]:
    note = db.session.query(Note).get(id)
    if note is None:
        return jsonify({'error': 'Note not found'}), 404
    return NoteDTO.from_note(note).to_json(), 200


@notes_bluprint.put('/<uuid:id>')
def edit_note(id: uuid) -> tuple[Response, int]:
    request_dto = NoteDTO(**request.get_json())
    if request_dto.id != id:
        return jsonify({'error': 'Id in URL does not match id in request body'}), 400

    persisted_note = db.session.query(Note).get(id)
    if persisted_note is not None:
        persisted_note.name = request_dto.name
        persisted_note.content = request_dto.content
        db.session.commit()
        return jsonify(NoteDTO.from_note(persisted_note).__dict__), 200
    else:
        return jsonify({'error': 'Note not found'}), 404


@notes_bluprint.delete('/<uuid:id>')
def delete_note(id: uuid) -> tuple[Response, int]:
    note = db.session.query(Note).get(id)
    if note is None:
        return jsonify({'error': 'Note not found'}), 404

    db.session.delete(note)
    db.session.commit()
    return Response(), 204
