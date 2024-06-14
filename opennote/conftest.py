import pytest

from opennote import create_app
from test_config import TestConfig


@pytest.fixture
def test_app():
    app = create_app(TestConfig())
    app.config.update({
        "TESTING": True
    })
    yield app


@pytest.fixture
def test_app_unauthorised():
    app = create_app(TestConfig(skip_auth=False))
    app.config.update({
        "TESTING": True
    })
    yield app
