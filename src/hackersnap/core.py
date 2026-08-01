"""hackersnap core — the one file you actually need to write.

The Item model and all four formatters below are DONE and tested. The only
function left to implement is `fetch()`: make the real request to Hacker News stories,
turn each result into an `Item`, and return the list. Delete the
NotImplementedError once it works.
"""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional

import httpx


@dataclass
class Item:
    """One thing from Hacker News stories — a story, post, repo event, feed entry…"""

    title: str
    url: str
    author: str = ""
    score: int = 0
    comments: int = 0
    created_at: Optional[datetime] = None
    body: str = ""

    def _created_iso(self) -> str:
        return self.created_at.isoformat() if self.created_at else ""


# --------------------------------------------------------------------------- #
# fetch — THE PART YOU WRITE. Everything below fetch is already finished.
# --------------------------------------------------------------------------- #

_STORY_ENDPOINTS = {
    "top": "topstories",
    "new": "newstories",
    "best": "beststories",
    "ask": "askstories",
    "show": "showstories",
    "job": "jobstories",
}

_HN_BASE = "https://hacker-news.firebaseio.com/v0"
_HN_ITEM_URL = "https://news.ycombinator.com/item?id={id}"


def fetch(query: Optional[str] = None, limit: int = 10) -> list[Item]:
    """Fetch up to *limit* stories from Hacker News.

    *query* selects the story list:
        top   – current top stories (default)
        new   – newest stories
        best  – all-time best
        ask   – Ask HN posts
        show  – Show HN posts
        job   – job listings

    Each story is fetched individually from the Firebase REST API; for large
    limits this is O(limit) requests but is fine for typical CLI usage (≤ 30).
    """
    kind = (query or "top").lower().strip()
    endpoint = _STORY_ENDPOINTS.get(kind, "topstories")

    with httpx.Client(
        timeout=20,
        headers={"User-Agent": "hackersnap/0.1.0 (github.com/rook-builds/hackersnap)"},
    ) as client:
        # Step 1: get the ordered list of story IDs
        resp = client.get(f"{_HN_BASE}/{endpoint}.json")
        resp.raise_for_status()
        ids: list[int] = resp.json() or []

        # Step 2: fetch each story up to the requested limit
        items: list[Item] = []
        for story_id in ids[: limit * 2]:  # over-fetch to account for dead/deleted
            if len(items) >= limit:
                break
            try:
                data = client.get(f"{_HN_BASE}/item/{story_id}.json").json()
            except Exception:
                continue

            if not data or data.get("deleted") or data.get("dead"):
                continue

            # Stories without a URL (Ask HN, Show HN text posts) get an HN link
            url = data.get("url") or _HN_ITEM_URL.format(id=story_id)

            # Unix timestamp → aware datetime
            created_at: Optional[datetime] = None
            if ts := data.get("time"):
                created_at = datetime.fromtimestamp(ts, tz=timezone.utc)

            items.append(
                Item(
                    title=data.get("title", ""),
                    url=url,
                    author=data.get("by", ""),
                    score=data.get("score", 0),
                    comments=data.get("descendants", 0),
                    created_at=created_at,
                    body=data.get("text", ""),
                )
            )

        return items


# --------------------------------------------------------------------------- #
# formatters — DONE. Tested by tests/test_formatter.py. Do not rewrite.
# --------------------------------------------------------------------------- #
def to_text(items: list[Item], source: str = "hackersnap") -> str:
    if not items:
        return f"# {source}\n\nNo items found."
    lines = [f"# {source}", ""]
    for i, it in enumerate(items, 1):
        meta = []
        if it.score:
            meta.append(f"{it.score} points")
        if it.comments:
            meta.append(f"{it.comments} comments")
        if it.author:
            meta.append(f"by {it.author}")
        suffix = f"  ({' · '.join(meta)})" if meta else ""
        lines.append(f"{i}. **{it.title}**{suffix}")
        if it.url:
            lines.append(f"   {it.url}")
        if it.body:
            lines.append(f"   {it.body}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def to_json(items: list[Item], source: str = "hackersnap") -> str:
    payload = {
        "source": source,
        "count": len(items),
        "items": [
            {**asdict(it), "created_at": it._created_iso()} for it in items
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def to_table(items: list[Item], source: str = "hackersnap") -> str:
    if not items:
        return "No items found."
    header = "| # | Title | Score | Comments | Author |"
    sep = "|---|-------|-------|----------|--------|"
    rows = [header, sep]
    for i, it in enumerate(items, 1):
        title = it.title.replace("|", "\\|")
        rows.append(
            f"| {i} | {title} | {it.score} | {it.comments} | {it.author} |"
        )
    return "\n".join(rows)


def to_csv(items: list[Item], source: str = "hackersnap") -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["title", "url", "author", "score", "comments", "created_at"])
    for it in items:
        w.writerow(
            [it.title, it.url, it.author, it.score, it.comments, it._created_iso()]
        )
    return buf.getvalue()
