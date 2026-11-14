#!/usr/bin/env python3
"""METASO video generation API: submit a request, inspect a task, download its result."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import urllib.error
import urllib.request
import uuid

BASE = "https://metaso.cn/api/minimax"
CREDENTIALS = Path.home() / ".config/metaso-video/credentials.json"
LEGACY_CREDENTIALS = Path.home() / ".config/metaso-h3/credentials.json"


def load_key():
    key = os.environ.get("METASO_API_KEY")
    if key:
        return key
    for path in (CREDENTIALS, LEGACY_CREDENTIALS):
        if path.exists():
            return json.loads(path.read_text())["api_key"]
    return None


def api(path, payload=None, body=None, content_type="application/json"):
    key = load_key()
    if not key:
        raise ValueError("未配置 METASO API Key。请参照技能说明在本机配置 METASO_API_KEY 或凭据文件；不要在聊天中发送密钥。")
    request = urllib.request.Request(
        BASE + path,
        data=body if body is not None else (json.dumps(payload).encode() if payload is not None else None),
        headers={"Authorization": "Bearer " + key, "Content-Type": content_type},
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


def upload(path):
    boundary = "metaso-" + uuid.uuid4().hex
    filename = path.name.replace('"', '_').replace('\r', '_').replace('\n', '_')
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="purpose"\r\n\r\nvideo_generation_input\r\n'
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            'Content-Type: application/octet-stream\r\n\r\n').encode() + path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
    result = api('/v1/files/upload', body=body, content_type='multipart/form-data; boundary=' + boundary)
    info = result.get('file') or {}
    if info.get('file_id') is not None:
        return {'url': 'mm_file://' + str(info['file_id'])}
    if info.get('download_url'):
        return {'url': info['download_url']}
    raise ValueError('Upload response has no file_id or download_url')


def validate_regeneration(payload):
    if payload.get('model') != 'MiniMax-H3' or payload.get('resolution') != '2K':
        raise ValueError('Regeneration requires MiniMax-H3 and 2K')
    task_id, content = payload.get('source_task_id'), payload.get('content')
    if bool(task_id) == bool(content):
        raise ValueError('Provide exactly one of source_task_id and content')
    if task_id and (not isinstance(task_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', task_id)):
        raise ValueError('Invalid source task ID')
    if content:
        if not isinstance(content, list) or any(not isinstance(item, dict) for item in content):
            raise ValueError('Invalid content')
        if sum(item.get('role') == 'base_video' and item.get('type') == 'video_url' for item in content) != 1:
            raise ValueError('Content requires exactly one base_video')
        if not any(item.get('type') == 'text' and item.get('text') for item in content):
            raise ValueError('Content requires the original prompt')


def validate(payload):
    model = payload.get("model")
    resolutions = {
        "MiniMax-H3": {"480p", "512p", "768P", "1080p", "2K"},
        "seedance-2.0-mini": {"480p", "720p"},
        "seedance-2.0-fast": {"480p", "720p"},
        "seedance-2.0": {"480p", "720p", "1080p", "4k"},
        "seedance-2.5": {"480p", "720p", "1080p"},
    }
    if model not in resolutions:
        raise ValueError("Unsupported model")
    resolution = payload.get("resolution")
    if resolution not in resolutions[model]:
        raise ValueError("Invalid resolution for the selected model")
    duration = payload.get("duration")
    maximum = 30 if model == "seedance-2.5" or (model == "MiniMax-H3" and resolution != "2K") else 15
    if type(duration) is not int or not 4 <= duration <= maximum:
        raise ValueError("Invalid duration for the selected model and resolution")
    if not isinstance(payload.get("content"), list) or not payload["content"]:
        raise ValueError("A nonempty content array is required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("request", type=Path, help="JSON request body")
    create.add_argument("--submit", action="store_true", help="Submit one billable task")
    regenerate = commands.add_parser("regenerate")
    source = regenerate.add_mutually_exclusive_group(required=True)
    source.add_argument("--task-id")
    source.add_argument("--request", type=Path)
    regenerate.add_argument("--submit", action="store_true", help="Submit one billable task")
    commands.add_parser("balance")
    upload_command = commands.add_parser("upload")
    upload_command.add_argument("file", type=Path)
    upload_command.add_argument("--submit", action="store_true", help="Upload the file to METASO")
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
    elif args.command == "regenerate":
        payload = json.loads(args.request.read_text()) if args.request else {"model": "MiniMax-H3", "source_task_id": args.task_id, "resolution": "2K"}
        validate_regeneration(payload)
        result = api("/v2/video_regeneration", payload) if args.submit else {"dry_run": True, "request": payload}
    elif args.command == "balance":
        result = api("/v2/credits/balance")
    elif args.command == "upload":
        if not args.file.is_file():
            raise ValueError("File not found")
        result = upload(args.file) if args.submit else {"dry_run": True, "file": str(args.file.resolve()), "bytes": args.file.stat().st_size}
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
