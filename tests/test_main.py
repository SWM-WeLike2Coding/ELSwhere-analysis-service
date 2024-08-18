from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_health_check():
    response = client.get("/health_check")
    assert response.status_code == 200
    assert response.json() == {"status": "It's Working in " + os.getenv('APPLICATION_NAME')}