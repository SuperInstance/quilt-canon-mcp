"""CLI for testing the MCP server directly."""
import argparse
import json
import sys

from .server import handle_request


def main():
    p = argparse.ArgumentParser(description="quilt-canon-mcp CLI tester")
    p.add_argument("method", help="MCP method (initialize, tools/list, tools/call, etc.)")
    p.add_argument("--tool", help="Tool name (for tools/call)")
    p.add_argument("--args", help="Tool args as JSON")
    p.add_argument("--uri", help="Resource URI (for resources/read)")
    args = p.parse_args()

    params = {}
    if args.tool:
        params["name"] = args.tool
        if args.args:
            params["arguments"] = json.loads(args.args)

    if args.uri:
        params["uri"] = args.uri

    req = {"jsonrpc": "2.0", "id": 1, "method": args.method, "params": params}
    resp = handle_request(req)
    print(json.dumps(resp, indent=2))


if __name__ == "__main__":
    main()
