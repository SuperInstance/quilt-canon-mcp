# quilt-canon-mcp

**MCP (Model Context Protocol) server exposing Quilt substrate walker canon as tools for AI agents.**

## Why this matters

Other AI agents (Claude, GPT, etc.) that support MCP can now directly query our canon — every doctrine, every cell, every JEV verification. The canon becomes a *tool* in someone else's toolkit.

## Quick start

### Run the MCP server

```bash
pip install -e .
quilt-canon-mcp
# Server listens on stdio. Send JSON-RPC 2.0 requests.
```

### Test via CLI

```bash
quilt-canon-mcp-cli initialize
quilt-canon-mcp-cli tools/list
quilt-canon-mcp-cli tools/call --tool list_doctrines
quilt-canon-mcp-cli tools/call --tool search_canon --args '{"query": "scar witness", "top_k": 3}'
quilt-canon-mcp-cli tools/call --tool probe_canon --args '{"lore_text": "The cell is a scar..."}'
```

### Use from any MCP client

```python
import json, subprocess

proc = subprocess.Popen(
    ["quilt-canon-mcp"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
)

req = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
       "params": {"name": "list_doctrines"}}
proc.stdin.write(json.dumps(req) + "\n")
proc.stdin.flush()
print(proc.stdout.readline())
```

## Tools exposed

| Tool | Description |
|------|-------------|
| `get_canon(name)` | Get a canon piece by name |
| `search_canon(query, top_k=5)` | Search canon lore |
| `list_doctrines()` | List the 5 bedrock doctrines |
| `get_canon_by_doctrine(doctrine)` | Pieces anchored to doctrine |
| `probe_canon(lore_text)` | JEV probe (composite + doctrines hit) |
| `list_canon()` | List all canon pieces |

## Resources exposed

- `canon://list` — all canon pieces
- `canon://doctrines` — the 5 bedrock doctrines

## Fleet integration

This tool **uses** the existing fleet as acceleration:

- **`quilt-multi-oracle`** — `probe_canon()` falls back to local heuristic; if `DEEPINFRA_TOKEN` is set, calls DeepInfra Llama-3.3-70B.
- **`quilt-canon-graph`** (sibling) — knowledge graph of canon
- **`quilt-canon-search`** (sibling) — TF-IDF search
- **`quilt-iterator`** — reference for canon structure
- **`quilt-bridge`** — translates canon across substrates

## The 5 bedrock doctrines

1. `cells_are_scars` — every cell records an attempted entry
2. `witness_log_is_prediction` — the log IS the prediction
3. `canon_gate_is_chord` — canon passes when multiple agents agree
4. `oracle_is_heard` — JEV probes canon with multi-model consensus
5. `substrate_quantum` — the substrate is the walker; canon is substrate-aware

## Polyformalism canary

```bash
python -m quilt_canon_mcp.canary
# → 0x024a555471370b18d
```

## License

MIT
