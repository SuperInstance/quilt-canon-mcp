"""Simple test runner (no pytest dep)."""
import sys
import importlib

sys.path.insert(0, "/workspace/repos/quilt-canon-mcp")

results = []
failures = []

def test(name, func):
    try:
        func()
        results.append((name, "PASS"))
    except AssertionError as e:
        results.append((name, f"FAIL: {e}"))
        failures.append(name)
    except Exception as e:
        results.append((name, f"ERROR: {type(e).__name__}: {e}"))
        failures.append(name)


# Load modules
import json
import quilt_canon_mcp.server as server
import quilt_canon_mcp.canary as canary_mod
import quilt_canon_mcp.loader as loader
import quilt_canon_mcp.search as search_mod
import quilt_canon_mcp.probe as probe_mod


def t_canary():
    assert canary_mod.canary() == "0x24a555471370b18d"


def t_init():
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    resp = server.handle_request(req)
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "canon-mcp"


def t_list_tools():
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = server.handle_request(req)
    names = [t["name"] for t in resp["result"]["tools"]]
    for n in ["get_canon", "search_canon", "list_doctrines", "probe_canon", "list_canon"]:
        assert n in names, f"missing tool: {n}"


def t_list_resources():
    req = {"jsonrpc": "2.0", "id": 3, "method": "resources/list"}
    resp = server.handle_request(req)
    uris = [r["uri"] for r in resp["result"]["resources"]]
    assert "canon://list" in uris
    assert "canon://doctrines" in uris


def t_list_doctrines():
    req = {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "list_doctrines"}}
    resp = server.handle_request(req)
    text = resp["result"]["content"][0]["text"]
    docs = json.loads(text)
    for d in loader.DOCTRINES:
        assert d in docs, f"missing doctrine: {d}"


def t_probe():
    lore = "A scar is a record that entry was attempted. The cell holds witness logs that predict the future."
    result = probe_mod.probe_lore(lore)
    assert result["composite"] > 0.4, f"composite too low: {result['composite']}"
    assert "cells_are_scars" in result["doctrines_hit"]


def t_search():
    results = search_mod.search_canon("scar witness", top_k=3)
    assert isinstance(results, list)
    for r in results:
        assert "name" in r and "score" in r


def t_unknown_tool():
    req = {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "unknown_xyz"}}
    resp = server.handle_request(req)
    assert "error" in resp


def t_unknown_method():
    req = {"jsonrpc": "2.0", "id": 6, "method": "weird/method"}
    resp = server.handle_request(req)
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def t_read_doctrines():
    req = {"jsonrpc": "2.0", "id": 7, "method": "resources/read", "params": {"uri": "canon://doctrines"}}
    resp = server.handle_request(req)
    text = resp["result"]["contents"][0]["text"]
    docs = json.loads(text)
    assert len(docs) == 5


test("test_canary", t_canary)
test("test_initialize", t_init)
test("test_list_tools", t_list_tools)
test("test_list_resources", t_list_resources)
test("test_list_doctrines_tool", t_list_doctrines)
test("test_probe_canon", t_probe)
test("test_search_canon", t_search)
test("test_unknown_tool", t_unknown_tool)
test("test_unknown_method", t_unknown_method)
test("test_read_resource", t_read_doctrines)

print("\n=== quilt-canon-mcp test results ===")
for name, status in results:
    print(f"  {status:60} {name}")

print(f"\n{len(results) - len(failures)}/{len(results)} passed")
if failures:
    sys.exit(1)
