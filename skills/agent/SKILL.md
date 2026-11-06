---
name: agent
description: Drive an interactive browser session — navigate, snapshot the page, click, type, scroll, handle logins, captchas, cookie banners, and multi-step automation that keeps state across steps. Use when a task needs more than a one-shot scrape/screenshot/pdf, e.g. logging in, filling multi-page forms, downloading files behind a flow, or exploring a site step by step.
---

# Browser Agent

This skill is backed by the **Browserless MCP server** (bundled with this plugin via `.mcp.json`), not a one-shot REST call. It can keep a live browser session when explicitly requested, so use it when the task is interactive or multi-step. For single-shot work prefer `/browserless:smart-scrape` (scrape, screenshot, pdf, links) instead.

## How to run it

Call the `browserless_agent` MCP tool. It connects to a real Chromium session at `https://mcp.browserless.io`. Request a page **snapshot** (accessibility tree + element refs) explicitly; do not assume each action returns one.

For a multi-step task, set `keepSessionAlive: true` on the **first call**. Without it, a new call with no session handle is one-shot and closes the browser when it finishes. Start with a `goto` and a `snapshot` in the same batch:

```json
{
  "keepSessionAlive": true,
  "commands": [
    { "method": "goto", "params": { "url": "https://example.com" } },
    { "method": "snapshot" }
  ]
}
```

Save the returned `sessionId` and pass it on **every continuation call**. Use refs from the latest snapshot, not invented or stale refs. For example, replace both placeholders below with the returned session ID and a clickable ref from that snapshot:

```json
{
  "sessionId": "<returned-session-id>",
  "commands": [
    { "method": "click", "params": { "selector": "<ref-from-latest-snapshot>" } },
    { "method": "snapshot" }
  ]
}
```

Passing `sessionId` keeps that browser alive by default; omitting it does not resume the session. Continue inspecting snapshots and acting until the goal is reached, then extract the result. End action batches with an explicit `snapshot` when you need the updated page state. When finished, close the browser with `{"sessionId":"<returned-session-id>","method":"close"}` rather than leaving it alive.

The agent handles the hard parts automatically — cookie consent, captchas, login flows, shadow DOM, modals, tabs, and file up/downloads. Let it; don't hand-roll those.

## When to use which

| Task | Use |
|------|-----|
| Read / extract one page | `/browserless:smart-scrape` |
| Screenshot or PDF one page | `/browserless:smart-scrape` (formats) |
| Search the web | `/browserless:search` |
| List/crawl a site's URLs | `/browserless:map`, `/browserless:crawl` |
| Run a fixed Puppeteer script | `/browserless:function` |
| **Log in, click through, fill forms, multi-step, stateful** | **`browserless_agent` (this skill)** |

## Auth

MCP uses the plugin's `headersHelper` (requires Python 3.9+) to read `~/.browserless/.env` on each connection. Run `/browserless:auth`, then reconnect Browserless in `/mcp`; saved credentials need no shell-profile exports or new launch terminal. Non-empty environment overrides apply when visible to the helper, but current Claude Code filters token-like environment variables from plugin helpers, so the saved file is the reliable MCP token source. Never display the helper's JSON output because it can contain credentials.

Valid `browserless.io` URLs, including SFO/LON/AMS, dedicated subdomains and trailing slashes, are passed through `x-browserless-api-url`. With no URL, MCP uses SFO. Arbitrary self-hosted URLs remain REST-only; the helper warns and omits that override, so hosted MCP uses SFO. With no token, the helper omits `Authorization`, allowing Claude Code to offer OAuth sign-in. An invalid configured token must be corrected or cleared before reconnecting; it does not fall back to OAuth.

If the `browserless_agent` tool isn't listed, the MCP server isn't connected — run `/mcp` to check, and ensure the plugin's `.mcp.json` is loaded.
