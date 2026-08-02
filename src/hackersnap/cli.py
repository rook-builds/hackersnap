"""hackersnap CLI — Turn Hacker News top stories into a clean markdown digest"""

import sys

import click

from .core import fetch, to_csv, to_json, to_table, to_text
from .introspect import get_introspect_json, get_skill_md

_ACLI_COMMANDS = {"introspect", "skill", "serve"}


def _handle_acli_command(cmd: str, host: str, port: int) -> None:
    if cmd == "introspect":
        print(get_introspect_json())
    elif cmd == "skill":
        print(get_skill_md())
    elif cmd == "serve":
        from .mcp_server import serve as run_serve

        run_serve(host=host, port=port)


@click.command()
@click.argument("query", required=False, default=None)
@click.option("--limit", "-n", default=10, show_default=True, help="How many items to fetch.")
@click.option(
    "--output",
    "-o",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json", "table", "csv"]),
    help="Output format.",
)
@click.option("--port", "-p", default=8080, show_default=True, help="Port for MCP server (serve mode).")
@click.option("--host", default="localhost", show_default=True, help="Host for MCP server (serve mode).")
def main(query, limit, output, port, host):
    """Turn Hacker News top stories into a clean markdown digest.

    \b
    Story types: top (default), new, best, ask, show, job
    Special commands: hackersnap introspect | hackersnap skill
    MCP server:       hackersnap serve [--port 8080] [--host localhost]
    """
    if query in _ACLI_COMMANDS:
        _handle_acli_command(query, host=host, port=port)
        sys.exit(0)

    items = fetch(query, limit=limit)

    if output == "text":
        click.echo(to_text(items))
    elif output == "json":
        click.echo(to_json(items))
    elif output == "table":
        click.echo(to_table(items))
    else:
        click.echo(to_csv(items), nl=False)


if __name__ == "__main__":
    main()
