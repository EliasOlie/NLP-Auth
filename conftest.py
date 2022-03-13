import pytest
import json
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture
def token() -> str:
    payload = json.dumps({
        "useremail": "test@test.com",
        "password": "123"
    })
    c = client.post('/security/login', payload)
    yield c.json()['token']
