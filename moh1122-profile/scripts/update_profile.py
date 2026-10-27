#!/usr/bin/env python3
"""Refresh public GitHub cards and activity using only the Python standard library.

Run from any directory with Python 3.10+. GITHUB_TOKEN is optional locally.
This script edits local files only; the workflow handles commits and pushes.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

USERNAME = "moh1122"
PROFILE_REPO = "moh1122/moh1122"
ROOT = Path(__file__).resolve().parents[1]
CARD_DIR = ROOT / "profile-summary-card-output" / "github_dark"
CARD_SERVICE = "https://github-profile-summary-cards.vercel.app/api/cards/"
CARDS = (
    ("0-profile-details.svg", "profile-details", USERNAME),
    ("1-repos-per-language.svg", "repos-per-language", "Top Languages by Repo"),
    ("2-most-commit-language.svg", "most-commit-language", "Top Languages by Commit"),
    ("3-stats.svg", "stats", "Total Stars"),
    ("4-productive-time.svg", "productive-time", "UTC +3"),
)
START = "<!--START_SECTION:activity-->"
END = "<!--END_SECTION:activity-->"
MAX_BYTES = 2_000_000


def fetch(url: str, *, github_api: bool = False) -> bytes:
    headers = {"User-Agent": "moh1122-profile-refresh"}
    if github_api:
        if urllib.parse.urlparse(url).netloc != "api.github.com":
            raise ValueError("GitHub credentials are restricted to api.github.com")
        headers["Accept"] = "application/vnd.github+json"
        headers["X-GitHub-Api-Version"] = "2026-03-10"
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Response exceeds the expected size")
    return data


def validate_svg(data: bytes, expected_text: str) -> None:
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("Unexpected XML declarations")
    root = ET.fromstring(data)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Card service did not return an SVG")
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1].lower()
        if tag in {"script", "foreignobject"}:
            raise ValueError("Unexpected active SVG content")
        if any(key.lower().startswith("on") for key in element.attrib):
            raise ValueError("Unexpected SVG event handler")
    text = " ".join(root.itertext())
    if expected_text not in text:
        raise ValueError("Card content does not match the requested profile or metric")
    if any(message in text.lower() for message in ("something went wrong", "rate limit exceeded", "user not found")):
        raise ValueError("The service returned an error card")


def download_card(card: tuple[str, str, str]) -> tuple[str, bytes]:
    filename, endpoint, expected_text = card
    query = {"username": USERNAME, "theme": "github_dark"}
    if endpoint == "productive-time":
        query["utcOffset"] = "3"
    data = fetch(CARD_SERVICE + endpoint + "?" + urllib.parse.urlencode(query))
    validate_svg(data, expected_text)
    return filename, data


def refresh_cards() -> None:
    # No files change until every response has downloaded and passed validation.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        cards = list(pool.map(download_card, CARDS))
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="profile-cards-", dir=CARD_DIR.parent) as staging:
        staged = Path(staging)
        for filename, data in cards:
            (staged / filename).write_bytes(data)
        for filename, _ in cards:
            (staged / filename).replace(CARD_DIR / filename)
    print("Refreshed all five profile cards.")


def read_public_events() -> list[dict]:
    events: list[dict] = []
    for page in range(1, 4):
        url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=100&page={page}"
        batch = json.loads(fetch(url, github_api=True))
        if not isinstance(batch, list):
            raise ValueError("GitHub did not return an events list")
        events.extend(batch)
        if len(batch) < 100:
            break
    return events


def activity_lines(events: list[dict], *, now: datetime | None = None) -> list[str]:
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=30)
    lines: list[str] = []
    seen: set[tuple] = set()
    for event in sorted(events, key=lambda item: item.get("created_at", ""), reverse=True):
        actor = event.get("actor", {}).get("login", "")
        repo = event.get("repo", {}).get("name", "")
        if actor.lower() != USERNAME or repo.lower() == PROFILE_REPO:
            continue
        if event.get("public") is not True or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            continue
        try:
            created = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        if created < cutoff:
            continue
        date = created.date().isoformat()
        repo_url = f"https://github.com/{repo}"
        link = f"[{repo}]({repo_url})"
        kind = event.get("type")
        payload = event.get("payload", {})
        detail = None
        number = None
        if kind == "PushEvent":
            detail = f"Pushed updates to {link}."
        elif kind == "PullRequestEvent":
            request = payload.get("pull_request", {})
            number = request.get("number") or payload.get("number")
            action = payload.get("action")
            verb = "Merged" if action == "closed" and request.get("merged") else {"opened": "Opened", "closed": "Closed", "reopened": "Reopened"}.get(action)
            if verb and isinstance(number, int):
                detail = f"{verb} [PR #{number}]({repo_url}/pull/{number}) in {link}."
        elif kind == "IssuesEvent":
            number = payload.get("issue", {}).get("number")
            verb = {"opened": "Opened", "closed": "Closed", "reopened": "Reopened"}.get(payload.get("action"))
            if verb and isinstance(number, int):
                detail = f"{verb} [issue #{number}]({repo_url}/issues/{number}) in {link}."
        elif kind == "ReleaseEvent" and payload.get("action") == "published":
            detail = f"Published a release in {link}."
        elif kind == "CreateEvent" and payload.get("ref_type") == "repository":
            detail = f"Created {link}."
        key = (kind, repo, date, number)
        if detail and key not in seen:
            seen.add(key)
            lines.append(f"- **{date}** — {detail}")
        if len(lines) == 5:
            break
    return lines or [f"Browse my [public GitHub activity](https://github.com/{USERNAME}) and [latest app releases](https://iosapps.cloud)."]


def refresh_activity() -> None:
    readme_path = ROOT / "README.md"
    content = readme_path.read_text(encoding="utf-8")
    if content.count(START) != 1 or content.count(END) != 1:
        raise ValueError("README activity markers are missing or duplicated")
    begin = content.index(START) + len(START)
    end = content.index(END)
    if end < begin:
        raise ValueError("README activity markers are in the wrong order")
    lines = activity_lines(read_public_events())
    updated = content[:begin] + "\n" + "\n".join(lines) + "\n" + content[end:]
    temporary = readme_path.with_suffix(".md.tmp")
    temporary.write_text(updated, encoding="utf-8")
    temporary.replace(readme_path)
    print("Refreshed recent public activity.")


def main() -> int:
    try:
        refresh_cards()
    except Exception as error:
        print(f"::warning::Cards were not refreshed; retaining the existing set. {type(error).__name__}: {error}")
        for filename, _, expected in CARDS:
            path = CARD_DIR / filename
            if not path.is_file():
                print(f"::error::No existing card available: {filename}")
                return 1
            validate_svg(path.read_bytes(), expected)
    try:
        refresh_activity()
    except Exception as error:
        print(f"::warning::Recent activity was not refreshed; retaining the previous text. {type(error).__name__}: {error}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
