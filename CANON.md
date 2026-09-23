# Canon — quilt-canon-mcp

## What this tool is

An MCP server that exposes Quilt canon lore as tools and resources for OTHER AI agents. Any agent that supports the Model Context Protocol can now query the canon directly — list doctrines, search lore, probe canon text via JEV.

## How it proves itself

**It runs.** `pip install -e .` then `quilt-canon-mcp` starts the server. JSON-RPC 2.0 over stdio. Tested with `tests/test_mcp.py` (8 tests).

**It polyformalisms.** The canary hash `0x024a555471370b18d` matches across the fleet's 7 ports (Python, JS, Rust, Bash, SQL, Go, Zig).

**It measures.** Every probe returns a composite score + doctrine anchors, derived deterministically locally OR via DeepInfra Llama-3.3-70B if `DEEPINFRA_TOKEN` is set.

## Doctrines it instantiates

- **canon_gate_is_chord** — the canon is gated by multi-model consensus
- **oracle_is_heard** — JEV probes canon; here the probe is exposed as an MCP tool
- **substrate_quantum** — the canon is substrate-aware; this tool adds the MCP substrate

## Tools

1. `get_canon(name)` — fetch canon lore
2. `search_canon(query, top_k)` — find canon by query
3. `list_doctrines()` — list the 5 bedrock doctrines
4. `get_canon_by_doctrine(doctrine)` — find pieces anchored to a doctrine
5. `probe_canon(lore_text)` — JEV probe (composite score, doctrines hit)
6. `list_canon()` — list all canon pieces

## Resources

- `canon://list` — JSON dump of all canon pieces
- `canon://doctrines` — the 5 bedrock doctrines

## Fleet usage

This tool *uses* the fleet — it doesn't reinvent:
- **quilt-multi-oracle** — `probe_canon()` calls DeepInfra via the multi-oracle chord pattern
- **quilt-canon-graph** (sibling) — knowledge graph view of canon
- **quilt-canon-search** (sibling) — TF-IDF search
- **quilt-iterator** — referenced for canon structure
- **quilt-bridge** — referenced for polyformalism
