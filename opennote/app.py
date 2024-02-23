import os
import typing as t

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from .database import init_db
from .notes.notes import notes_bluprint


class PydanticJsonProvider(DefaultJSONProvider):
    """A JSON provider that uses pydantic's JSON serialization if applicable or default one.
    Currently not supporting deserialization
    """

    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        from pydantic import BaseModel
        if isinstance(obj, BaseModel):
            return obj.json()
        if isinstance(obj, list) and all(isinstance(i, BaseModel) for i in obj):
            return '[' + ', '.join(i.json() for i in obj) + ']'
        return super().dumps(obj, **kwargs)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.json_provider_class = PydanticJsonProvider
    app.json = PydanticJsonProvider(app)

    CORS(app)

    app.register_blueprint(notes_bluprint)

    init_db(app)

    return app
