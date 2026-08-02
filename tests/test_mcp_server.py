"""Unit tests for hackersnap.mcp_server.

All tests target handle_mcp_request() — the pure function at the heart of the
server — so we never need a real HTTP server or real HN network calls.
"""
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from hackersnap.core import Item
from hackersnap.mcp_server import handle_mcp_request

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

SAMPLE_ITEMS = [
    Item(
        title="An interesting story",
        url="https://example.com/story",
        author="testuser",
        score=100,
        comments=42,
        created_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
    ),
    Item(
        title="Another story",
        url="https://example.com/another",
        author="otheruser",
        score=50,
        comments=10,
    ),
]


def _list_req(req_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "method": "tools/list"}


def _call_req(name: str = "fetch", arguments: dict | None = None, req_id: int = 1) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments or {}},
    }


# --------------------------------------------------------------------------- #
# tools/list
# --------------------------------------------------------------------------- #


def test_tools_list_returns_result():
    resp = handle_mcp_request(_list_req())
    assert "result" in resp
    assert "error" not in resp


def test_tools_list_has_fetch_tool():
    resp = handle_mcp_request(_list_req())
    tools = resp["result"]["tools"]
    assert len(tools) >= 1
    assert tools[0]["name"] == "fetch"


def test_tools_list_has_input_schema():
    resp = handle_mcp_request(_list_req())
    schema = resp["result"]["tools"][0]["inputSchema"]
    assert "query" in schema["properties"]
    assert "limit" in schema["properties"]


def test_tools_list_schema_has_enum():
    resp = handle_mcp_request(_list_req())
    schema = resp["result"]["tools"][0]["inputSchema"]
    enum = schema["properties"]["query"]["enum"]
    assert set(enum) == {"top", "new", "best", "ask", "show", "job"}


def test_tools_list_preserves_id():
    resp = handle_mcp_request(_list_req(req_id=77))
    assert resp["id"] == 77


# --------------------------------------------------------------------------- #
# tools/call
# --------------------------------------------------------------------------- #


def test_tools_call_fetch_returns_text_content():
    with patch("hackersnap.mcp_server.fetch", return_value=SAMPLE_ITEMS):
        resp = handle_mcp_request(_call_req())
    assert "result" in resp
    content = resp["result"]["content"]
    assert len(content) >= 1
    assert content[0]["type"] == "text"
    assert "An interesting story" in content[0]["text"]


def test_tools_call_passes_query_and_limit():
    with patch("hackersnap.mcp_server.fetch", return_value=SAMPLE_ITEMS) as mock_fetch:
        handle_mcp_request(_call_req(arguments={"query": "best", "limit": 5}))
    mock_fetch.assert_called_once_with(query="best", limit=5)


def test_tools_call_default_args():
    with patch("hackersnap.mcp_server.fetch", return_value=SAMPLE_ITEMS) as mock_fetch:
        handle_mcp_request(_call_req(arguments={}))
    mock_fetch.assert_called_once_with(query="top", limit=10)


def test_tools_call_preserves_id():
    with patch("hackersnap.mcp_server.fetch", return_value=SAMPLE_ITEMS):
        resp = handle_mcp_request(_call_req(req_id=42))
    assert resp["id"] == 42


@pytest.mark.parametrize("kind", ["top", "new", "best", "ask", "show", "job"])
def test_tools_call_all_story_types(kind):
    with patch("hackersnap.mcp_server.fetch", return_value=SAMPLE_ITEMS):
        resp = handle_mcp_request(_call_req(arguments={"query": kind}))
    assert "result" in resp, f"Expected result for query={kind!r}"
    assert "error" not in resp


# --------------------------------------------------------------------------- #
# Error paths
# --------------------------------------------------------------------------- #


def test_unknown_tool_returns_error():
    resp = handle_mcp_request(_call_req(name="nonexistent"))
    assert "error" in resp
    assert resp["error"]["code"] == -32601
    assert "nonexistent" in resp["error"]["message"]


def test_unknown_method_returns_error():
    resp = handle_mcp_request({"jsonrpc": "2.0", "id": 1, "method": "unknown/method"})
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_missing_method_returns_error():
    resp = handle_mcp_request({"jsonrpc": "2.0", "id": 1})
    assert "error" in resp


def test_error_preserves_id():
    resp = handle_mcp_request({"jsonrpc": "2.0", "id": 55, "method": "bad/method"})
    assert resp["id"] == 55
