import os
import typing as t
from os import environ

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from sqlalchemy import URL

from opennote.auth import auth
from opennote.auth.auth_filter import creat_auth_filter
from opennote.common.error_handling import register_error_handlers
from opennote.notes import notes
from .database import init_db
from .test_config import AppTestConfig


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


def create_app(test_config: AppTestConfig = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.json_provider_class = PydanticJsonProvider
    app.json = PydanticJsonProvider(app)

    CORS(app)

    app.register_blueprint(notes.bluprint)
    app.register_blueprint(auth.bluprint_auth)
    app.register_blueprint(auth.bluprint_users)

    if not (test_config and test_config.skip_auth):
        app.before_request(creat_auth_filter(bypass_prefixes=[auth.URL_PREFIX]))

    register_error_handlers(app)

    if test_config and test_config.test_database_url:
        init_db(app, test_config.test_database_url)
    else:
        init_db(app, URL.create(drivername="postgresql",
                                host="localhost",
                                database="yana",
                                username=environ.get("DB_USERNAME"),
                                password=environ.get("DB_PASSWORD")))

    app.config['JWT_SECRET'] = os.environ.get("JWT_SECRET")

    auth.init_starting_data(app)

    return app
