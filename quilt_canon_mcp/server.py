"""MCP (Model Context Protocol) server exposing Quilt canon lore as tools.

Implements JSON-RPC 2.0 over stdio per the MCP spec.
Reference: https://modelcontextprotocol.io/
"""
import json
import sys
from typing import Any, Dict, List

from .loader import DOCTRINES, get_by_doctrine, get_by_name, load_canon
from .probe import probe_lore
from .search import search_canon


PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "canon-mcp", "version": "0.1.0"}


def list_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "get_canon",
            "description": "Get a canon piece by name (file stem or title).",
            "inputSchema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "search_canon",
            "description": "Search canon lore. Returns top-k matches with score.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "list_doctrines",
            "description": "List all 5 bedrock canon doctrines.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_canon_by_doctrine",
            "description": "Return canon pieces anchored to a doctrine.",
            "inputSchema": {
                "type": "object",
                "properties": {"doctrine": {"type": "string"}},
                "required": ["doctrine"],
            },
        },
        {
            "name": "probe_canon",
            "description": "Probe lore text via the JEV oracle. Returns composite + doctrines hit.",
            "inputSchema": {
                "type": "object",
                "properties": {"lore_text": {"type": "string"}},
                "required": ["lore_text"],
            },
        },
        {
            "name": "list_canon",
            "description": "List all canon pieces (titles only).",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def list_resources() -> List[Dict[str, Any]]:
    return [
        {
            "uri": "canon://list",
            "name": "All canon pieces",
            "description": "List of every canon piece (titles + doctrines)",
            "mimeType": "application/json",
        },
        {
            "uri": "canon://doctrines",
            "name": "Bedrock doctrines",
            "description": "The 5 bedrock canon doctrines",
            "mimeType": "application/json",
        },
    ]


def handle_tool_call(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments", {})

    if name == "get_canon":
        canon = get_by_name(args.get("name", ""))
        if canon is None:
            return {"error": {"code": -1, "message": f"canon piece '{args.get('name')}' not found"}}
        return {"content": [{"type": "text", "text": json.dumps(canon.to_dict(), indent=2)}]}

    elif name == "search_canon":
        results = search_canon(args.get("query", ""), args.get("top_k", 5))
        return {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}

    elif name == "list_doctrines":
        return {"content": [{"type": "text", "text": json.dumps(DOCTRINES, indent=2)}]}

    elif name == "get_canon_by_doctrine":
        pieces = get_by_doctrine(args.get("doctrine", ""))
        return {"content": [{"type": "text", "text": json.dumps([p.to_dict() for p in pieces], indent=2)}]}

    elif name == "probe_canon":
        result = probe_lore(args.get("lore_text", ""))
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "list_canon":
        pieces = load_canon()
        out = [{"name": p.name, "title": p.title, "doctrines_hit": p.doctrines_hit} for p in pieces]
        return {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]}

    return {"error": {"code": -1, "message": f"unknown tool: {name}"}}


def handle_read_resource(params: Dict[str, Any]) -> Dict[str, Any]:
    uri = params.get("uri", "")

    if uri == "canon://list":
        pieces = load_canon()
        out = [{"name": p.name, "title": p.title, "doctrines_hit": p.doctrines_hit} for p in pieces]
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(out, indent=2)}]}

    elif uri == "canon://doctrines":
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(DOCTRINES, indent=2)}]}

    return {"error": {"code": -1, "message": f"unknown resource: {uri}"}}


def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": SERVER_INFO,
            },
        }

    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": list_tools()}}

    elif method == "tools/call":
        result = handle_tool_call(req.get("params", {}))
        if "error" in result:
            return {"jsonrpc": "2.0", "id": req_id, "error": result["error"]}
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    elif method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": list_resources()}}

    elif method == "resources/read":
        result = handle_read_resource(req.get("params", {}))
        if "error" in result:
            return {"jsonrpc": "2.0", "id": req_id, "error": result["error"]}
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }


def run_server():
    """Run the MCP server over stdio. JSON-RPC 2.0 line-delimited."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_server()
