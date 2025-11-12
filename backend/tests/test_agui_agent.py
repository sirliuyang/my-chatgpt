# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import os
import sys
import types
from fastapi import FastAPI
from fastapi.testclient import TestClient
import importlib

# --- Ensure env vars exist before importing modules that read settings ---
os.environ.setdefault("OPENAI_API_KEY", "test-api-key")
os.environ.setdefault("OPENAI_BASE_URL", "https://api.test-openai.local")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# --- Inject minimal fake pydantic_ai modules so imports in target module succeed ---
fake_ag_ui_mod = types.ModuleType("pydantic_ai.ag_ui")


async def _placeholder_handle_ag_ui_request(*, request, agent):
    from fastapi import Response
    return Response(content="agui-ok", media_type="text/plain")


fake_ag_ui_mod.handle_ag_ui_request = _placeholder_handle_ag_ui_request

fake_ui_agui_mod = types.ModuleType("pydantic_ai.ui.ag_ui")


class FakeAGUIAdapter:
    @staticmethod
    async def dispatch_request(request, agent=None):
        from fastapi.responses import JSONResponse
        return JSONResponse({"status": "ok"})


fake_ui_agui_mod.AGUIAdapter = FakeAGUIAdapter

sys.modules["pydantic_ai.ag_ui"] = fake_ag_ui_mod
sys.modules["pydantic_ai.ui.ag_ui"] = fake_ui_agui_mod

# --- Import module under test ---
chat_agui_module = importlib.import_module("src.api.v1.endpoints.agui_agent")
router = getattr(chat_agui_module, "router")


def test_agui_agent_success_and_unauthorized(monkeypatch):
    """
    - Success: override get_current_user via app.dependency_overrides to return a valid user.
    - Unauthorized: override get_current_user to return None -> 401.
    """
    app = FastAPI()
    app.include_router(router)

    # Fake agent
    fake_agent_obj = object()
    monkeypatch.setattr(chat_agui_module, "get_or_create_agent", lambda: fake_agent_obj)

    # Monkeypatch handle_ag_ui_request to controlled async function
    async def fake_handle_ag_ui_request(request, agent):
        from fastapi import Response
        assert agent is fake_agent_obj
        return Response(content="AGUI RESPONSE", media_type="text/plain")

    monkeypatch.setattr(chat_agui_module, "handle_ag_ui_request", fake_handle_ag_ui_request)

    client = TestClient(app)

    # --- SUCCESS CASE ---
    async def fake_get_current_user():
        return {"id": 1, "username": "tester"}

    app.dependency_overrides[chat_agui_module.get_current_user] = fake_get_current_user

    resp = client.post("/agui/agent", json={"foo": "bar"})
    assert resp.status_code == 200
    assert resp.text == "AGUI RESPONSE"

    # --- UNAUTHORIZED CASE ---
    async def fake_get_current_user_none():
        return None

    app.dependency_overrides[chat_agui_module.get_current_user] = fake_get_current_user_none

    resp2 = client.post("/agui/agent", json={"foo": "bar"})
    assert resp2.status_code == 401
    assert "Invalid token" in resp2.json().get("detail", "")


def test_deferred_results_various(monkeypatch):
    """
    - Success: override get_current_user to valid user, patch AGUIAdapter.dispatch_request to return JSONResponse {'ok': True}.
    - Invalid JSON: send non-JSON body -> 400
    - Unauthorized: current_user None -> 401
    """
    app = FastAPI()
    app.include_router(router)

    # Fake agent
    monkeypatch.setattr(chat_agui_module, "get_or_create_agent", lambda: object())

    # Patch AGUIAdapter.dispatch_request
    async def fake_dispatch_request(request, agent=None):
        from fastapi.responses import JSONResponse
        return JSONResponse({"deferred": "ok"})

    if hasattr(chat_agui_module, "AGUIAdapter"):
        monkeypatch.setattr(chat_agui_module.AGUIAdapter, "dispatch_request", fake_dispatch_request)
    else:
        chat_agui_module.AGUIAdapter = types.SimpleNamespace(dispatch_request=fake_dispatch_request)

    client = TestClient(app)

    # --- SUCCESS CASE ---
    async def fake_get_current_user():
        return {"id": 2, "username": "u2"}

    app.dependency_overrides[chat_agui_module.get_current_user] = fake_get_current_user

    payload = {"deferred_results": [{"tool_call_id": "t1", "approval": True}]}
    resp = client.post("/agui/deferred_results", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"deferred": "ok"}

    # --- INVALID JSON CASE ---
    resp_invalid = client.post("/agui/deferred_results", data="not-a-json", headers={"content-type": "text/plain"})
    assert resp_invalid.status_code == 400

    # --- UNAUTHORIZED CASE ---
    async def fake_get_current_user_none():
        return None

    app.dependency_overrides[chat_agui_module.get_current_user] = fake_get_current_user_none

    resp_unauth = client.post("/agui/deferred_results", json=payload)
    assert resp_unauth.status_code == 401
    assert "Invalid token" in resp_unauth.json().get("detail", "")
