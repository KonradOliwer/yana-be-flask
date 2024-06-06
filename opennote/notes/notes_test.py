import json
import uuid


def test_notes_get_returns_empty_list_when_no_notes_created(test_app):
    with test_app.test_client() as client:
        response = client.get('/notes/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0


def test_notes_post_allows_adding_new_notes(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        post_data = json.loads(post_response.data)
        assert post_data.get('name') == "name1"
        assert post_data.get('content') == "content1"

        get_response = client.get('/notes/')
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        assert isinstance(get_data, list)
        assert len(get_data) == 1
        assert get_data[0].get('name') == "name1"
        assert get_data[0].get('content') == "content1"


def test_notes_post_fails_on_adding_note_with_existing_name(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        post_data = json.loads(post_response.data)
        assert post_data.get('name') == "name1"

        post_response = client.post('/notes/', json={"name": "name1", "content": "content2"})
        assert post_response.status_code == 400
        post_data = json.loads(post_response.data)
        assert post_data.get('code') == "NOTE_ALREADY_EXISTS"
        assert post_data.get('message') is None


def test_notes_put_updates_note(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        post_data = json.loads(post_response.data)
        assert post_data.get('name') == "name1"
        assert post_data.get('content') == "content1"

        note_id = post_data.get('id')
        put_response = client.put('/notes/' + note_id,
                                  json={"id": note_id, "name": "updatedName", "content": "updatedContent"})
        assert put_response.status_code == 200
        put_data = json.loads(put_response.data)
        assert put_data.get('id') == note_id
        assert put_data.get('name') == "updatedName"
        assert put_data.get('content') == "updatedContent"

        get_response = client.get('/notes/')
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        assert isinstance(get_data, list)
        assert len(get_data) == 1
        assert get_data[0].get('name') == "updatedName"
        assert get_data[0].get('content') == "updatedContent"


def test_notes_put_fails_on_attempt_to_add_not_existing_entity(test_app):
    with test_app.test_client() as client:
        note_id = uuid.uuid1()
        put_response = client.put('/notes/' + str(note_id),
                                  json={"id": note_id, "name": "updatedName", "content": "updatedContent"})
        assert put_response.status_code == 404
        put_data = json.loads(put_response.data)
        assert put_data.get('code') == "NOTE_NOT_FOUND"
        assert put_data.get('message') is None


def test_notes_get_shows_multiple_notes(test_app):
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
        assert get_data[0].get('name') == "name1"
        assert get_data[0].get('content') == "content1"
        assert get_data[1].get('name') == "name2"
        assert get_data[1].get('content') == "content2"


def test_post_note_fails_on_too_long_name(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "a" * 51, "content": "content1"})
        assert post_response.status_code == 400
        post_data = json.loads(post_response.data)
        assert post_data.get('code') == "NOTE_VALIDATION_ERROR"
        assert post_data.get('message') == "name: String should have at most 50 characters"


def test_put_note_fails_on_too_long_name(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        note_id = json.loads(post_response.data).get('id')
        put_response = client.put('/notes/' + note_id,
                                  json={"id": note_id, "name": "a" * 51, "content": "updatedContent"})
        assert put_response.status_code == 400
        put_data = json.loads(put_response.data)
        assert put_data.get('code') == "NOTE_VALIDATION_ERROR"
        assert put_data.get('message') == "name: String should have at most 50 characters"


def test_put_note_fails_on_different_id_then_in_url(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        note_id = json.loads(post_response.data).get('id')
        put_response = client.put('/notes/' + note_id,
                                  json={"id": uuid.uuid1(), "name": "updatedName", "content": "updatedContent"})
        assert put_response.status_code == 400
        put_data = json.loads(put_response.data)
        assert put_data.get('code') == "NOTE_VALIDATION_ERROR"
        assert put_data.get('message') == 'id: should match url id'


def test_notes_post_for_existing_note_name(test_app):
    with test_app.test_client() as client:
        post_response = client.post('/notes/', json={"name": "name1", "content": "content1"})
        assert post_response.status_code == 201
        post_response = client.post('/notes/', json={"name": "name1", "content": "content2"})
        assert post_response.status_code == 400
        post_data = json.loads(post_response.data)
        assert post_data.get('code') == "NOTE_ALREADY_EXISTS"
