import json


def test_register_requires_unique_username(test_app):
    with test_app.test_client() as client:
        response1 = client.post('/users/', json={"username":"test name","password":"test password1"})
        assert response1.status_code == 201
        response2 = client.post('/users/', json={"username":"test name","password":"test password2"})
        assert response2.status_code == 400
        body2 = json.loads(response2.data)
        assert body2['code'] == "VALIDATION_ERROR"


def test_registered_user_can_log_in(test_app):
    with test_app.test_client() as client:
        create_user_response = client.post('/users/', json={"username":"test name","password":"test password"})
        assert create_user_response.status_code == 201

        login_response = client.post('/access-token/', json={"username":"test name","password":"test password"})
        assert login_response.status_code == 200
        login_body = json.loads(login_response.data)
        assert login_body['token'].startswith('Bearer ')
