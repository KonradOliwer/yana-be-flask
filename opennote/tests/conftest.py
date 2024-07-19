import os

import pytest
from flask_migrate import upgrade

from opennote.app import create_app
from opennote.test_config import AppTestConfig


@pytest.fixture(scope="session", autouse=True)
def setup():
    os.environ["FLASK_APP"] = "opennote/app.py"
    os.environ["DB_PASSWORD"] = "password"
    os.environ["DB_USERNAME"] = "user"
    os.environ["JWT_SECRET"] = "secret"


@pytest.fixture
def test_app():
    app = create_app(AppTestConfig())
    with app.app_context():
        upgrade()
    yield app


@pytest.fixture
def test_app_unauthorised():
    app = create_app(AppTestConfig(skip_auth=False))
    with app.app_context():
        upgrade()
    yield app
