import typing as t

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from pydantic import ValidationError
from sqlalchemy import URL
from sqlalchemy.exc import IntegrityError

from common.error_handling import ClientError, handle_client_error, handle_validation_error, handle_integrity_error
from .database import init_db
from .notes.notes import notes_bluprint


class PydanticJsonProvider(DefaultJSONProvider):
    """A JSON provider that uses pydantic's JSON serialization if applicable or default one.
    Currently not supporting deserialization
    """

    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        try:
            return obj.model_dump_json()
        except AttributeError:
            try:
                return '[' + ', '.join(i.model_dump_json() for i in obj) + ']'
            except AttributeError:
                return super().dumps(obj, **kwargs)


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.json_provider_class = PydanticJsonProvider
    app.json = PydanticJsonProvider(app)

    CORS(app)

    app.register_blueprint(notes_bluprint)
    app.register_error_handler(ClientError, handle_client_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(IntegrityError, handle_integrity_error)

    if test_config:
        init_db(app, test_config.db_url)
    else:
        init_db(app, URL.create(drivername="postgresql",
                                host="localhost",
                                database="yana",
                                username="user",
                                password="password"))

    return app
