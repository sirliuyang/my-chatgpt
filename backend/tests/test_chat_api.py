# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
# tests/test_chat_api.py
import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
import importlib
import pytest

# Ensure env vars exist before importing project modules (avoid pydantic Settings errors)
os.environ.setdefault("OPENAI_API_KEY", "test-api-key")
os.environ.setdefault("OPENAI_BASE_URL", "https://api.test-openai.local")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

chat_module = importlib.import_module("src.api.v1.endpoints.chat_api")
router = getattr(chat_module, "router")


def test_chat_endpoint_streams_and_saves(monkeypatch):
    """
    Synchronous test using TestClient:
    - monkeypatch internal symbols in chat_module (conversation, create_message, stream_chat_response)
    - ensure SSE contains yielded chunks and that create_message was called for user and assistant
    """
    # 1) Fake conversation.create_conversation_if_not_exists to always return an id
    fake_conv_id = 42
    fake_conv = type("C", (), {"create_conversation_if_not_exists": lambda db, cid: fake_conv_id})
    monkeypatch.setattr(chat_module, "conversation", fake_conv)

    # 2) Capture create_message calls in a list (synchronous)
    saved_messages = []

    def fake_create_message(db, conversation_id, role, content):
        saved_messages.append({"conversation_id": conversation_id, "role": role, "content": content})

    monkeypatch.setattr(chat_module, "create_message", fake_create_message)

    # 3) Fake stream_chat_response: async generator yielding two chunks then ending
    async def fake_stream_chat_response(full_history):
        assert isinstance(full_history, list)
        yield "Hello"
        await asyncio.sleep(0)  # maintain asynchronous behavior
        yield " world"

    monkeypatch.setattr(chat_module, "stream_chat_response", fake_stream_chat_response)

    # 4) Ensure get_messages_by_conversation is None so we use provided history
    monkeypatch.setattr(chat_module, "get_messages_by_conversation", None, raising=False)

    # Build temporary FastAPI app and include router
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    # Override dependencies: get_db and get_current_user
    def fake_get_db():
        # yield-like behavior not necessary for sync TestClient; returning None is fine
        return None

    def fake_get_current_user():
        return {"id": 1, "username": "test"}

    app.dependency_overrides[chat_module.get_db] = fake_get_db
    app.dependency_overrides[chat_module.get_current_user] = fake_get_current_user

    client = TestClient(app)

    payload = {
        "conversation_id": None,
        "message": "User asks something",
        "history": [
            {"role": "user", "content": "previous question"},
            {"role": "assistant", "content": "previous answer"},
        ],
    }

    # Use stream=True to iterate server-sent events progressively (TestClient will run the ASGI app)
    with client.stream("POST", "/api/v1/chat", json=payload, timeout=20.0) as resp:
        assert resp.status_code == 200
        # Collect streamed bytes/chunks
        collected = []
        for chunk in resp.iter_lines():
            if not chunk:
                continue
            # chunk is bytes; decode if needed
            if isinstance(chunk, bytes):
                chunk = chunk.decode("utf-8", errors="ignore")
            collected.append(chunk)

    combined = "\n".join(collected)
    # Ensure yielded deltas are present
    assert "Hello" in combined
    assert "world" in combined or " world" in combined
    assert "[DONE]" in combined or "DONE" in combined

    # Assertions on saved messages
    roles = [m["role"] for m in saved_messages]
    assert "user" in roles
    assert "assistant" in roles
    assistant_msgs = [m for m in saved_messages if m["role"] == "assistant"]
    assert assistant_msgs, "assistant message not saved"
    assert "Hello" in assistant_msgs[-1]["content"]
    assert "world" in assistant_msgs[-1]["content"]


def test_chat_endpoint_unauthorized(monkeypatch):
    """
    If get_current_user returns None, endpoint should return 401.
    """
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    def fake_get_db():
        return None

    def fake_get_current_user_none():
        return None

    app.dependency_overrides[chat_module.get_db] = fake_get_db
    app.dependency_overrides[chat_module.get_current_user] = fake_get_current_user_none

    client = TestClient(app)

    payload = {
        "conversation_id": None,
        "message": "should be unauthorized",
        "history": [],
    }

    resp = client.post("/api/v1/chat", json=payload, timeout=10.0)
    assert resp.status_code == 401
    data = resp.json()
    assert "Invalid token" in data.get("detail", "")
