from fastapi.testclient import TestClient
from app.main import app


def test_public_site_is_a_published_aggregate():
    with TestClient(app) as client:
        response = client.get('/api/v1/site')
        assert response.status_code == 200
        data = response.json()
        assert data['content']['profile']['full_name'] == 'Gagandeep Kaur'
        assert data['content']['education'][0]['result_value'] == '9.24'
        assert len(data['content']['projects']) == 2
        assert 'phone_e164' not in data['content']['profile']


def test_private_draft_requires_owner_session():
    with TestClient(app) as client:
        response = client.get('/api/v1/admin/draft')
        assert response.status_code == 401
        assert response.json()['error']['code'] == 'AUTH_REQUIRED'
