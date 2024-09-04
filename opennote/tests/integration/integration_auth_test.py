import re

from opennote.auth.jwt import JWT
from opennote.database import db
from opennote.db_model import RefreshToken


def test_login_creates_refresh_token(test_app):
    with test_app.test_client() as client:
        response = client.post('/users/', json={"username": "test", "password": "test"})
        assert response.status_code == 201

        response = client.post('/access-token/login', method='POST', json={"username": "test", "password": "test"})
        assert response.status_code == 201

        set_cookie_header = response.headers['Set-Cookie']
        pattern = r"Authorization=Bearer ([\S]+); HttpOnly; SameSite=Strict; Secure; Path=\/;"
        token_value = re.match(pattern, set_cookie_header).groups()[0]
        jwt = JWT.from_string(token_value)

        refresh_token = db.session.query(RefreshToken).get(jwt.refresh_token)

        assert refresh_token is not None
        assert refresh_token.user_id == jwt.user_id
        assert refresh_token.active
        assert refresh_token.expire_at > jwt.expire_at


def test_preform_token_refresh_creates_new_refresh_token(test_app):
    with test_app.test_client() as client:
        response = client.post('/users/', json={"username": "test", "password": "test"})
        assert response.status_code == 201
        response = client.post('/access-token/login', method='POST', json={"username": "test", "password": "test"})
        assert response.status_code == 201

        response = client.post('/access-token/refresh', method='POST', json={"username": "test", "password": "test"})
        assert response.status_code == 201
        set_cookie_header = response.headers['Set-Cookie']
        pattern = r"Authorization=Bearer ([\S]+); HttpOnly; SameSite=Strict; Secure; Path=\/;"
        token_value = re.match(pattern, set_cookie_header).groups()[0]
        jwt = JWT.from_string(token_value)

        refresh_tokens = db.session.query(RefreshToken).filter_by(user_id=jwt.user_id).all()
        assert len(refresh_tokens) == 2
        active_token = next((rt for rt in refresh_tokens if rt.active), None)
        deactivated_token = next((rt for rt in refresh_tokens if not rt.active), None)
        assert active_token is not None
        assert deactivated_token is not None
        assert active_token.expire_at >= deactivated_token.expire_at
