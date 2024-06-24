import pytest

from opennote.app import create_app
from opennote.test_config import AppTestConfig


@pytest.fixture
def test_app():
    app = create_app(AppTestConfig())
    app.config.update({
        "TESTING": True
    })
    yield app


@pytest.fixture
def test_app_unauthorised():
    app = create_app(AppTestConfig(skip_auth=False))
    app.config.update({
        "TESTING": True
    })
    yield app
