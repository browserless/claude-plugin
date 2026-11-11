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

Passing `sessionId` keeps that browser alive by default; omitting it does not resume the session. Continue inspecting snapshots and acting until the goal is reached, then extract the result. End action batches with an explicit `snapshot` when you need the updated page state. When finished, close the browser rather than leaving it alive:

```json
{
  "sessionId": "<returned-session-id>",
  "commands": [{ "method": "close" }]
}
```

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

The MCP server authenticates with the plugin's options, not with `~/.browserless/.env`:

- **Browserless API token** (`browserless_token`): required. Claude Code stores it in your system's secure credential store and sends it as the `Authorization` header.
- **Browserless API URL** (`api_url`): the hosted region, sent as `x-browserless-api-url`. Defaults to SFO (`https://production-sfo.browserless.io`). Use `https://production-lon.browserless.io`, `https://production-ams.browserless.io`, or another `https://*.browserless.io` URL such as a dedicated deployment. The hosted MCP server rejects self-hosted URLs, so keep those for the REST skills only.

To set or change them, run `/plugin configure browserless@browserless`, then restart Claude Code or reconnect Browserless in `/mcp` to apply them. From a shell, pipe a JSON object to `claude plugin configure browserless@browserless --values-stdin`. Never print the token.

If the `browserless_agent` tool isn't listed, the MCP server isn't connected. Claude Code doesn't start the Browserless server until the required API token is set, so if Browserless is missing from `/mcp`, run `/plugin configure browserless@browserless`, enter the token, and restart Claude Code or reconnect in `/mcp`.

If `/mcp` reports that the server rejected the configured Authorization header, the token is invalid, or the API URL option isn't an `https://*.browserless.io` URL. Set it with `/plugin configure browserless@browserless` and reconnect. Because the plugin always sends an `Authorization` header, Claude Code doesn't offer OAuth sign-in for this server.
