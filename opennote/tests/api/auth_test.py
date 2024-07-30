import json
import re


def test_whoami_require_auth(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.get('/users/whoami')
        assert response.status_code == 403


def test_create_user_require_auth(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.post('/users/', json={"username": "test name", "password": "test password"})
        assert response.status_code == 403


def test_refresh_token_require_jwt(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.post('/access-token/refresh', json={"username": "test name", "password": "test password"})
        assert response.status_code == 403


def test_register_requires_unique_username(test_app):
    with test_app.test_client() as client:
        response1 = client.post('/users/', json={"username": "test name", "password": "test password1"})
        assert response1.status_code == 201
        response2 = client.post('/users/', json={"username": "test name", "password": "test password2"})
        assert response2.status_code == 400
        body2 = json.loads(response2.data)
        assert body2['code'] == "VALIDATION_ERROR"


def test_registered_user_can_log_in(test_app):
    with test_app.test_client() as client:
        create_user_response = client.post('/users/', json={"username": "test name", "password": "test password"})
        assert create_user_response.status_code == 201

        login_response = client.post('/access-token/create', json={"username": "test name", "password": "test password"})
        assert login_response.status_code == 201
        assert json.loads(login_response.data)['token_expire_at'] is not None

        set_cookie_header = login_response.headers['Set-Cookie']
        pattern = r"Authorization=Bearer [\S]+\.[\S]+\.[\S]+; HttpOnly; SameSite=Strict; Secure; Path=\/; Max-Age=1800"
        assert re.match(pattern, set_cookie_header) is not None, f"Set-Cookie doesn't included correct auth token, instead it contains: {set_cookie_header}"


def test_login_with_wrong_password(test_app):
    with test_app.test_client() as client:
        create_user_response = client.post('/users/', json={"username": "test name", "password": "test password"})
        assert create_user_response.status_code == 201

        login_response = client.post('/access-token/create', json={"username": "test name", "password": "wrong password"})
        assert login_response.status_code == 403


def test_login_with_non_existing_user(test_app):
    with test_app.test_client() as client:
        login_response = client.post('/access-token/create', json={"username": "non existing user", "password": "wrong password"})
        assert login_response.status_code == 403


def test_login_with_wrong_username(test_app):
    with test_app.test_client() as client:
        create_user_response = client.post('/users/', json={"username": "test name", "password": "test password"})
        assert create_user_response.status_code == 201

        login_response = client.post('/access-token/create', json={"username": "wrong username", "password": "test password"})
        assert login_response.status_code == 403


def test_login_and_use_token(test_app):
    with test_app.test_client() as client:
        create_user_response = client.post('/users/', json={"username": "test name", "password": "test password"})
        assert create_user_response.status_code == 201

        login_response = client.post('/access-token/create', json={"username": "test name", "password": "test password"})
        assert login_response.status_code == 201

        response = client.get('/notes/')
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body == []


def test_whoami_happy_path(test_app):
    with test_app.test_client() as client:
        create_user_response = client.post('/users/', json={"username": "test name", "password": "test password"})
        assert create_user_response.status_code == 201

        login_response = client.post('/access-token/create', json={"username": "test name", "password": "test password"})
        assert login_response.status_code == 201

        response = client.get('/users/whoami')
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body['username'] == "test name"


def test_refresh_token_creates_new_token(test_app):
    with test_app.test_client() as client:
        create_user_response = client.post('/users/', json={"username": "test name", "password": "test password"})
        assert create_user_response.status_code == 201

        login_response = client.post('/access-token/create', json={"username": "test name", "password": "test password"})
        login_body = json.loads(login_response.data)
        assert login_response.status_code == 201

        refresh_login = client.post('/access-token/refresh')
        assert refresh_login.status_code == 201
        refresh_body = json.loads(refresh_login.data)
        assert refresh_body['token_expire_at'] is not None
        # since value in second, it's possible it will end up being created for same second
        assert refresh_body['token_expire_at'] >= login_body['token_expire_at']

        set_cookie_header = refresh_login.headers['Set-Cookie']
        pattern = r"Authorization=Bearer [\S]+\.[\S]+\.[\S]+; HttpOnly; SameSite=Strict; Secure; Path=\/; Max-Age=1800"
        assert re.match(pattern, set_cookie_header) is not None, f"Set-Cookie doesn't included correct auth token, instead it contains: {set_cookie_header}"
        assert set_cookie_header != login_response.headers['Set-Cookie']