# Changelog

## [0.2.0] - 2026-08-02

### Added
- `hackersnap serve [--port 8080] [--host localhost]` — starts a stateless MCP HTTP server
- Implements MCP 2026-07-28 specification (single `POST /mcp` per request, no session state)
- `tools/list` endpoint returns JSON Schema for the `fetch` tool
- `tools/call fetch` endpoint calls `core.fetch()` and returns a markdown digest
- `GET /mcp` health check returns name, version, spec version
- `handle_mcp_request()` pure function — fully unit-testable without a real server
- Updated `introspect` and `skill` commands to document the `serve` subcommand
- 14 new unit tests in `tests/test_mcp_server.py`
- Zero new runtime dependencies — server uses Python stdlib only

## [0.1.0] - 2026-08-01

### Added
- `hackersnap [top|new|best|ask|show|job]` — six story types via HN Firebase REST API
- `--limit N` — control story count (default 10)
- `--output [text|json|table|csv]` — four output modes
- `hackersnap introspect` — ACLI-compliant JSON capability description
- `hackersnap skill` — agentskills.io-compliant SKILL.md
- Graceful handling of dead/deleted stories
- Ask/Show HN posts without URLs get direct HN item links
