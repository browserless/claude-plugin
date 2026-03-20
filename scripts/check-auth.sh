#!/usr/bin/env bash
# SessionStart hook: check if Browserless authentication is configured

if [ -n "$BROWSERLESS_TOKEN" ]; then
  exit 0
fi

if [ -f "$HOME/.browserless/.env" ]; then
  exit 0
fi

echo "Browserless API token not configured. Run /browserless:auth to set up your API token." >&2
exit 0
