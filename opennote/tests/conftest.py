import os

import pytest
from flask_migrate import upgrade

from auth.auth import register, RegisterRequest, login, LoginRequest
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
    yield app


@pytest.fixture
def test_app_with_auth_filter():
    app = create_app(AppTestConfig(skip_auth=False))
    yield app
