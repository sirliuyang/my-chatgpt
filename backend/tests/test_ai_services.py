# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
# tests/test_ai_services.py
"""
Simplified unit tests for src.services.ai_service.

- Ensure required environment variables exist BEFORE importing the module to avoid pydantic Settings ValidationError.
- Only test pure, synchronous helper functions (_compute_delta and _extract_text_from_partial).
- Do not require pytest-asyncio or other async plugins.
"""

import os
import json
import pytest

# --- Ensure env vars exist before importing the tested module ---
os.environ.setdefault("OPENAI_API_KEY", "test-api-key")
os.environ.setdefault("OPENAI_BASE_URL", "https://api.test-openai.local")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# Now safe to import module (it will read settings without raising)
import src.services.ai_service as ai_service


# -----------------------
# Tests for _compute_delta
# -----------------------
@pytest.mark.parametrize(
    "prev,new,expected",
    [
        ("", "hello", "hello"),  # prev empty -> return whole new
        ("hello", "hello world", " world"),  # new startswith prev
        ("hello", "oh hello world", " world"),  # prev occurs inside new -> suffix after occurrence
        ("abcd", "xxabcdyy", "yy"),  # prev in middle -> return after prev
        ("abc", "zxy", "zxy"),  # no overlap -> return entire new
        ("abcde", "cdef", "f"),  # partial overlap -> return suffix after overlap
        ("same", "same", ""),  # identical -> no new suffix
        ("prefix", "", ""),  # new empty -> empty
    ],
)
def test_compute_delta_various(prev, new, expected):
    assert ai_service._compute_delta(prev, new) == expected


# -----------------------
# Tests for _extract_text_from_partial
# -----------------------
def test_extract_from_dict_with_content():
    partial = {"content": "This is text", "meta": 123}
    assert ai_service._extract_text_from_partial(partial) == "This is text"


def test_extract_from_dict_without_content():
    partial = {"foo": "bar", "num": 1}
    text = ai_service._extract_text_from_partial(partial)
    # Should be a JSON string representing the dict; parse back to assert content
    loaded = json.loads(text)
    assert loaded["foo"] == "bar"
    assert loaded["num"] == 1


def test_extract_from_pydantic_like_object():
    class Dummy:
        def __init__(self, content):
            self._content = content

        def dict(self):
            return {"content": self._content}

    obj = Dummy("pydantic-text")
    assert ai_service._extract_text_from_partial(obj) == "pydantic-text"


def test_extract_from_string_and_nonstring():
    assert ai_service._extract_text_from_partial("plain string") == "plain string"
    # integer fallback to str
    assert ai_service._extract_text_from_partial(123) == "123"
