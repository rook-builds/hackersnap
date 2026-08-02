"""Agent-CLI introspection: `hackersnap introspect` and `hackersnap skill`.

Lets any AI agent discover how to drive this tool without a human in the loop.
"""
import json

from . import __version__


def get_introspect_json() -> str:
    return json.dumps(
        {
            "name": "hackersnap",
            "version": __version__,
            "description": "Turn Hacker News top stories into a clean markdown digest",
            "commands": [
                {
                    "usage": "hackersnap [TARGET] --limit N --output text|json|table|csv",
                    "description": (
                        "Fetch HN stories.  TARGET is one of: top (default), new, best, "
                        "ask, show, job."
                    ),
                },
                {
                    "usage": "hackersnap serve --port 8080 --host localhost",
                    "description": (
                        "Start a stateless MCP HTTP server (2026-07-28 spec).  "
                        "Accepts POST /mcp with tools/list or tools/call (fetch tool)."
                    ),
                },
                {
                    "usage": "hackersnap introspect",
                    "description": "Print ACLI-compliant capability JSON.",
                },
                {
                    "usage": "hackersnap skill",
                    "description": "Print agentskills.io-compliant SKILL.md.",
                },
            ],
        },
        indent=2,
    )


def get_skill_md() -> str:
    return (
        "# hackersnap\n\n"
        "Turn Hacker News top stories into a clean markdown digest\n\n"
        "## Usage\n\n"
        "```\n"
        "hackersnap [TARGET] --limit 10 --output json\n"
        "hackersnap serve --port 8080\n"
        "```\n\n"
        "TARGET is one of: `top` (default), `new`, `best`, `ask`, `show`, `job`.\n\n"
        "Outputs: text (default), json, table, csv.\n\n"
        "## MCP server\n\n"
        "```\n"
        "hackersnap serve --port 8080 --host localhost\n"
        "```\n\n"
        "Starts a stateless MCP HTTP server (2026-07-28 spec) at `POST /mcp`.\n"
        "Supports `tools/list` and `tools/call` with the `fetch` tool.\n"
        "Zero extra dependencies — uses Python stdlib only.\n"
    )
