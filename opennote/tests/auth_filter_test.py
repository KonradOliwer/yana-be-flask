import json

from uuid import uuid4

from auth.jwt import JWT, timestamp_in_seconds


def test_auth_filter_happy_path(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.post('/access-token/', json={"username":"admin","password":"admin"})
        assert response.status_code == 201
        body = json.loads(response.data)
        token = body["token"]
        response = client.get('/notes/', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200


def test_no_bearer(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.post('/access-token/', json={"username":"admin","password":"admin"})
        assert response.status_code == 201
        body = json.loads(response.data)
        token = body["token"]
        response = client.get('/notes/', headers={'Authorization': f'{token}'})
        assert response.status_code == 403


def test_no_token(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.get('/notes/', headers={'Authorization': f'Bearer '})
        assert response.status_code == 403


def test_non_deserializable_token(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.get('/notes/', headers={'Authorization': f'Bearer abc'})
        assert response.status_code == 403


def test_no_auth_header(test_app_with_auth_filter):
    with test_app_with_auth_filter.test_client() as client:
        response = client.get('/notes/')
        assert response.status_code == 403


def test_auth_filter_happy_path_with_locally_created_jwt(test_app_with_auth_filter):
    with test_app_with_auth_filter.app_context():
        token = JWT(issued_at=timestamp_in_seconds(), token_id=uuid4(), algorith=JWT.SUPPORTED_ALGORITHM).serialize()
        with test_app_with_auth_filter.test_client() as client:
            response = client.get('/notes/', headers={'Authorization': f'Bearer {token}'})
            assert response.status_code == 200


def test_auth_filter_invalid_tempered_token(test_app_with_auth_filter):
    with test_app_with_auth_filter.app_context():
        old_token_issued_at = timestamp_in_seconds()
        old_token = JWT(issued_at=old_token_issued_at, token_id=uuid4(), algorith=JWT.SUPPORTED_ALGORITHM).serialize()
        jwt = JWT.from_string(old_token)
        jwt.issued_at = old_token_issued_at - 1
        new_token = jwt.serialize()
        with test_app_with_auth_filter.test_client() as client:
            response = client.get('/notes/', headers={'Authorization': f'Bearer {new_token}'})
            assert response.status_code == 403