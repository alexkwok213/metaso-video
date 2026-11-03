#!/usr/bin/env python3
"""METASO H3 API: submit a request, inspect a task, download its result."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import urllib.error
import urllib.request

BASE = "https://metaso.cn/api/minimax"
CREDENTIALS = Path.home() / ".config/metaso-h3/credentials.json"


def api(path, payload=None):
    key = os.environ.get("METASO_API_KEY")
    if not key and CREDENTIALS.exists():
        key = json.loads(CREDENTIALS.read_text())["api_key"]
    if not key:
        raise ValueError("METASO API key is not configured")
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        message = error.read().decode(errors="replace").replace(key, "[REDACTED]")
        raise ValueError(f"HTTP {error.code}: {message[:2000]}") from None
    base = result.get("base_resp") or {}
    if base.get("status_code", 0) != 0:
        raise ValueError(str(base))
    return result


def validate(payload):
    if payload.get("model") != "MiniMax-H3":
        raise ValueError("This integration uses model MiniMax-H3")
    resolution = payload.get("resolution")
    if resolution not in {"480p", "768P", "1080p", "2K"}:
        raise ValueError("Invalid resolution")
    duration = payload.get("duration")
    if type(duration) is not int or not 4 <= duration <= (15 if resolution == "2K" else 30):
        raise ValueError("Invalid duration for the selected resolution")
    if not isinstance(payload.get("content"), list) or not payload["content"]:
        raise ValueError("A nonempty content array is required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("request", type=Path, help="JSON request body")
    create.add_argument("--submit", action="store_true", help="Submit one billable task")
    for name in ("status", "download"):
        command = commands.add_parser(name)
        command.add_argument("task_id")
        if name == "download":
            command.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        payload = json.loads(args.request.read_text())
        validate(payload)
        result = api("/v2/video_generation", payload) if args.submit else {"dry_run": True, "request": payload}
    else:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", args.task_id):
            raise ValueError("Invalid task ID")
        result = api("/v2/query/video_generation/" + args.task_id)
        if args.command == "download":
            url = ((result.get("task") or {}).get("content") or {}).get("url")
            if not url or not url.startswith("https://"):
                raise ValueError("Task has no HTTPS video result yet")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            # No API credential is forwarded to the result host.
            with urllib.request.urlopen(url, timeout=60) as source, args.output.open("xb") as dest:
                shutil.copyfileobj(source, dest)
            result = {"task_id": args.task_id, "output": str(args.output.resolve()), "bytes": args.output.stat().st_size}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, urllib.error.URLError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
