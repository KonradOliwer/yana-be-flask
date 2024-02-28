import typing as t

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from sqlalchemy import URL

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


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.json_provider_class = PydanticJsonProvider
    app.json = PydanticJsonProvider(app)

    CORS(app)

    app.register_blueprint(notes_bluprint)


    app.config['SQLALCHEMY_ECHO'] = True

    if test_config:
        init_db(app, test_config.db_url)
    else:
        init_db(app, URL.create(drivername="postgresql",
                                host="localhost",
                                database="opennote",
                                username="user",
                                password="password"))

    return app
