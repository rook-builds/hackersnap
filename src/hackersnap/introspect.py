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
                    "description": "Turn Hacker News top stories into a clean markdown digest",
                }
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
        "```\n\n"
        "Outputs: text (default), json, table, csv.\n"
    )
