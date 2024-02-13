import uuid
from flask import Blueprint, jsonify, request

from opennote.db import db_session
from opennote.models import Note

notes_bluprint = Blueprint('notes', __name__, url_prefix='/notes')


class NoteDTO:
    def __init__(self, id: uuid, name: str, content: str):
        self.id = id
        self.name = name
        self.content = content

    @classmethod
    def from_note(cls, note: Note):
        return cls(note.id, note.name, note.content)

    @classmethod
    def from_json(cls, json):
        return cls(json.get('id', None), json['name'], json['content'])

    def to_note(self):
        return Note(self.id or uuid.uuid1(), self.name, content=self.content)

    def to_json(self):
        return jsonify(self.__dict__)


@notes_bluprint.route('/', methods=['GET'])
def get_all_notes():
    return jsonify(eqtls=[NoteDTO.from_note(note).to_json() for note in db_session.query(Note).all()]), 200


@notes_bluprint.route('/', methods=['POST'])
def post_note():
    request_dto = NoteDTO.from_json(request.get_json())
    request_note = request_dto.to_note()
    if request_dto.id is not None:
        persisted_note = db_session.query(Note).get(request_dto.id)
        if persisted_note is not None:
            persisted_note.name = request_note.name
            persisted_note.content = request_note.content
            db_session.commit()
            return NoteDTO.from_note(persisted_note).to_json(), 200

    db_session.add(request_note)
    db_session.commit()
    return NoteDTO.from_note(request_note).to_json(), 201


@notes_bluprint.route('/<uuid:id>', methods=['GET'])
def get_note(id):
    note = db_session.query(Note).get(id)
    if note is None:
        return jsonify({'error': 'Note not found'}), 404
    return NoteDTO.from_note(note).to_json(), 200
