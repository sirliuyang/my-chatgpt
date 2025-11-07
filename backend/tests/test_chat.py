# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_chat_endpoint():
    response = client.post("/api/v1/chat", json={"history": [], "message": "Hello"})
    assert response.status_code == 200
    # Further tests for streaming, but basic
