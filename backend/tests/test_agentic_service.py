# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
"""
Unit tests for src.services.agentic_service.get_or_create_agent

- Injects a lightweight fake `pydantic_ai` package before importing the target module so tests
  do not depend on the real pydantic_ai / OpenAI libraries.
- Ensures required env vars are set before module import (to satisfy Settings).
- Tests singleton behavior and the registered `tool_search` behavior with/without DDGS.
"""

import os
import sys
import types
import pytest

# Ensure env vars so src.common.config.Settings won't raise during import
os.environ.setdefault("OPENAI_API_KEY", "test-api-key")
os.environ.setdefault("OPENAI_BASE_URL", "https://api.test-openai.local")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# ----------------------------
# Create a fake pydantic_ai package
# ----------------------------
fake_pkg = types.ModuleType("pydantic_ai")


# Minimal RunContext placeholder
class RunContext:
    pass


# Fake Agent implementation that supports @agent.tool(name=...) decorator
class FakeAgent:
    def __init__(self, model=None, system_prompt=None, output_type=None):
        self.model = model
        self.system_prompt = system_prompt
        self.output_type = output_type
        # store registered tools as name -> function
        self._tools = {}

    def tool(self, name: str = None):
        # returns a decorator that registers the function under the given name
        def decorator(fn):
            key = name or fn.__name__
            self._tools[key] = fn
            return fn

        return decorator


# Attach to fake package
fake_pkg.Agent = FakeAgent
fake_pkg.RunContext = RunContext

# Create fake submodules: pydantic_ai.models.openai and pydantic_ai.providers.openai
models_module = types.ModuleType("pydantic_ai.models")
models_openai = types.ModuleType("pydantic_ai.models.openai")
providers_module = types.ModuleType("pydantic_ai.providers")
providers_openai = types.ModuleType("pydantic_ai.providers.openai")


# Minimal placeholder classes for imported names
class FakeOpenAIChatModel:
    def __init__(self, model_name=None, provider=None):
        self.model_name = model_name
        self.provider = provider


class FakeOpenAIProvider:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key


models_openai.OpenAIChatModel = FakeOpenAIChatModel
providers_openai.OpenAIProvider = FakeOpenAIProvider

# Insert into sys.modules so imports in target module resolve to our fakes
sys.modules["pydantic_ai"] = fake_pkg
sys.modules["pydantic_ai.models"] = models_module
sys.modules["pydantic_ai.models.openai"] = models_openai
sys.modules["pydantic_ai.providers"] = providers_module
sys.modules["pydantic_ai.providers.openai"] = providers_openai

# ----------------------------
# Now import the module under test
# ----------------------------
import importlib

agentic_service = importlib.import_module("src.services.agentic_service")

# Ensure we start tests with fresh singleton
agentic_service._agent_singleton = None


# ----------------------------
# Tests
# ----------------------------

def test_get_or_create_agent_singleton():
    """
    Ensure get_or_create_agent returns the same object on repeated calls.
    """
    a1 = agentic_service.get_or_create_agent()
    a2 = agentic_service.get_or_create_agent()
    assert a1 is a2
    # And our fake Agent must expose the _tools mapping (registered tools)
    assert isinstance(a1, FakeAgent)
    assert "tool_search" in a1._tools


@pytest.mark.asyncio
async def test_tool_search_when_ddgs_missing():
    """
    When DDGS is None (not installed), the registered tool_search should return
    the expected "not installed" message.
    """
    # Ensure DDGS is None to exercise that branch
    agentic_service.DDGS = None

    # recreate agent so the tool_search is re-registered (clear singleton)
    agentic_service._agent_singleton = None
    agent = agentic_service.get_or_create_agent()

    # Retrieve the registered tool function
    tool_fn = agent._tools.get("tool_search")
    assert tool_fn is not None, "tool_search must be registered"

    # call the async tool function
    res = await tool_fn(agentic_service.RunContext(), "some query", max_results=3)
    assert isinstance(res, str)
    assert "DDGS library not installed" in res


@pytest.mark.asyncio
async def test_tool_search_with_fake_ddgs():
    """
    When DDGS is available and returns sample results, tool_search should format them.
    """

    # Provide a Fake DDGS implementation
    class FakeDDGS:
        def text(self, query, max_results=5):
            # Return an iterable/list of dict-like results similar to duckduckgo_search
            return [
                {"title": "Title One", "href": "https://example.one", "body": "Snippet one"},
                {"heading": "Title Two", "link": "https://example.two", "snippet": "Snippet two"},
            ]

    agentic_service.DDGS = FakeDDGS

    # recreate agent to ensure fresh registration
    agentic_service._agent_singleton = None
    agent = agentic_service.get_or_create_agent()
    tool_fn = agent._tools.get("tool_search")
    assert tool_fn is not None

    out = await tool_fn(agentic_service.RunContext(), "python testing", max_results=2)
    # The output should contain formatted blocks with 标题:, 链接:, 摘要:
    assert "标题:" in out
    assert "链接:" in out
    assert "摘要:" in out
    # It should contain our fake URLs
    assert "https://example.one" in out or "https://example.two" in out
