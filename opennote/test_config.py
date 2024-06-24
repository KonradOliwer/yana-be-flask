from dataclasses import dataclass


@dataclass
class AppTestConfig:
    test_database_url: str = "sqlite:///:memory:"
    skip_auth: bool = True
