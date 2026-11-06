#!/usr/bin/env python3
"""Emit connect-time MCP headers without executing the saved credentials file."""
import json
import os
from pathlib import Path
import shlex
import sys
from urllib.parse import urlsplit


def main():
    saved = {}
    config = Path.home() / ".browserless" / ".env"
    try:
        lines = config.read_text().splitlines()
    except FileNotFoundError:
        lines = []
    for line in lines:
        key, separator, value = line.strip().removeprefix("export ").partition("=")
        key = key.strip()
        if not separator or key not in ("BROWSERLESS_TOKEN", "BROWSERLESS_API_URL"):
            continue
        parts = shlex.split(value, comments=True)
        if len(parts) > 1:
            raise ValueError("Saved values containing spaces must be quoted")
        saved[key] = parts[0] if parts else ""

    token = (os.environ.get("BROWSERLESS_TOKEN", "").strip()
             or saved.get("BROWSERLESS_TOKEN", "").strip())
    api_url = (os.environ.get("BROWSERLESS_API_URL", "").strip()
               or saved.get("BROWSERLESS_API_URL", "").strip())
    headers = {}
    if token:
        if any(ord(char) < 32 or ord(char) == 127 for char in token):
            raise ValueError("Invalid token")
        headers["Authorization"] = "Bearer " + token
    if api_url:
        url = urlsplit(api_url)
        # Match the hosted server's URL boundary, not just its three regions.
        if (len(api_url) > 2048 or any(ord(char) < 33 for char in api_url)
                or url.scheme not in ("http", "https") or not url.hostname
                or url.username or url.password or "\\" in api_url
                or "?" in api_url or "#" in api_url):
            raise ValueError("Invalid API URL")
        _ = url.port  # Reject malformed or out-of-range ports.
        if url.hostname == "browserless.io" or url.hostname.endswith(".browserless.io"):
            if url.scheme != "https":
                raise ValueError("Hosted API URL must use HTTPS")
            headers["x-browserless-api-url"] = api_url.rstrip("/")
        else:
            print("Custom API URL is REST-only; hosted MCP will use SFO.", file=sys.stderr)
    print(json.dumps(headers))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never include credential values or file contents in diagnostics.
        print("Cannot load MCP credentials; check ~/.browserless/.env and environment overrides.", file=sys.stderr)
        sys.exit(1)
