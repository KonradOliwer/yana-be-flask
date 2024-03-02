import json


def test_notes_get_endpoint_returns_empty_list_when_no_notes_created(test_app):
    with test_app.test_client() as client:
        response = client.get('/notes/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0


def test_notes_post_endpoint_allows_adding_new_notes(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        post_data = json.loads(post_response.data)
        assert post_data['name'] == "name1"
        assert post_data['content'] == "content1"

        get_response = client.get('/notes/')
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        assert isinstance(get_data, list)
        assert len(get_data) == 1
        assert get_data[0]['name'] == "name1"
        assert get_data[0]['content'] == "content1"


def test_notes_post_endpoint_allows_updating_note_by_name(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        post_data = json.loads(post_response.data)
        assert post_data['name'] == "name1"
        assert post_data['content'] == "content1"

        post_response = client.post('/notes/', json={"name": "name1", "content": "updatedContent"})
        assert post_response.status_code == 200
        post_data = json.loads(post_response.data)
        assert post_data['name'] == "name1"
        assert post_data['content'] == "updatedContent"

        get_response = client.get('/notes/')
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        assert isinstance(get_data, list)
        assert len(get_data) == 1
        assert get_data[0]['name'] == "name1"
        assert get_data[0]['content'] == "updatedContent"


def test_notes_get_endpoint_shows_multiple_notes(test_app):
    with test_app.test_client() as client:
        post_response1 = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response1.status_code == 201
        post_response2 = client.post('/notes/', json={"name": "name2", "content": "content2"})
        assert post_response2.status_code == 201

        get_response = client.get('/notes/')
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        assert isinstance(get_data, list)
        assert len(get_data) == 2
        assert get_data[0]['name'] == "name1"
        assert get_data[0]['content'] == "content1"
        assert get_data[1]['name'] == "name2"
        assert get_data[1]['content'] == "content2"


def test_post_note_fails_on_too_long_name(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "a" * 51, "content": "content1"})
        assert post_response.status_code == 400
        post_data = json.loads(post_response.data)
        assert post_data['code'] == "NOTE_VALIDATION_ERROR"
        assert post_data['message'] == "name: String should have at most 50 characters"