import datetime

from uuid import uuid4

from opennote import create_app
from opennote.auth.jwt import JWT


def test_encrypted_match_decrypted():
    with create_app().app_context():  # Use the application context
        issued_at = int(datetime.datetime(2024, 1, 1).timestamp())
        token_id = uuid4()
        user_id = uuid4()

        token: JWT = JWT.create(issued_at=issued_at, token_id=token_id, user_id=user_id)
        result_token = JWT.from_string(token.serialize())

        assert result_token.expire_at == issued_at + JWT.TIME_TO_LIVE
        assert result_token.token_id == token_id
        assert result_token.user_id == user_id
        assert result_token.algorith == "RS256"
        result_token.validate()
