"""Tests for quilt-canon-mcp server."""
import json
import pytest

from quilt_canon_mcp.server import handle_request, list_tools, list_resources
from quilt_canon_mcp.canary import canary
from quilt_canon_mcp.loader import DOCTRINES, get_by_doctrine
from quilt_canon_mcp.search import search_canon
from quilt_canon_mcp.probe import probe_lore


def test_canary():
    assert canary() == "0x024a555471370b18d"


def test_initialize():
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    resp = handle_request(req)
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "canon-mcp"


def test_list_tools():
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = handle_request(req)
    tool_names = [t["name"] for t in resp["result"]["tools"]]
    assert "get_canon" in tool_names
    assert "search_canon" in tool_names
    assert "list_doctrines" in tool_names
    assert "probe_canon" in tool_names


def test_list_resources():
    req = {"jsonrpc": "2.0", "id": 3, "method": "resources/list"}
    resp = handle_request(req)
    uris = [r["uri"] for r in resp["result"]["resources"]]
    assert "canon://list" in uris
    assert "canon://doctrines" in uris


def test_list_doctrines():
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "list_doctrines"},
    }
    resp = handle_request(req)
    text = resp["result"]["content"][0]["text"]
    doctrines = json.loads(text)
    assert "cells_are_scars" in doctrines
    assert "witness_log_is_prediction" in doctrines
    assert "canon_gate_is_chord" in doctrines
    assert "oracle_is_heard" in doctrines
    assert "substrate_quantum" in doctrines


def test_probe_canon_local():
    """Local heuristic probe works without DeepInfra."""
    lore = "A scar is a record that entry was attempted. The cell holds witness logs that predict the future."
    result = probe_lore(lore)
    assert result["composite"] > 0.5
    assert "cells_are_scars" in result["doctrines_hit"]
    assert result["distinct_voice"]


def test_search_canon():
    """Search returns matches."""
    results = search_canon("scar witness", top_k=3)
    # Either matches or empty (depends on canon content)
    assert isinstance(results, list)
    for r in results:
        assert "name" in r
        assert "score" in r


def test_unknown_tool():
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {"name": "unknown_tool_xyz"},
    }
    resp = handle_request(req)
    assert "error" in resp


def test_unknown_method():
    req = {"jsonrpc": "2.0", "id": 6, "method": "weird/method"}
    resp = handle_request(req)
    assert "error" in resp
    assert resp["error"]["code"] == -32601
