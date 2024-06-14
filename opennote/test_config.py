from dataclasses import dataclass


@dataclass
class TestConfig:
    test_database_url: str = "sqlite:///:memory:"
    skip_auth: bool = True
