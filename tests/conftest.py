import pytest

from opennote import create_app


class TestConfig:
    db_url = "sqlite:///:memory:"


@pytest.fixture()
def app():
    app = create_app(TestConfig())
    app.config.update({
        "TESTING": True,
    })
    yield app