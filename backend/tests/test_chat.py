# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_chat_endpoint():
    response = client.post("/api/v1/chat", json={"message": "Hello", "history": []})
    assert response.status_code == 200  # Note: Streaming, so test accordingly
    # Add more assertions as needed
