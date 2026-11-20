---
name: agent
description: Drive an interactive browser session — navigate, snapshot the page, click, type, scroll, handle logins, captchas, cookie banners, and multi-step automation that keeps state across steps. Use when a task needs more than a one-shot scrape/screenshot/pdf, e.g. logging in, filling multi-page forms, downloading files behind a flow, or exploring a site step by step.
---

# Browser Agent

This skill is backed by the **Browserless MCP server** (bundled with this plugin via `.mcp.json`), not a one-shot REST call. It can keep a live browser session when explicitly requested, so use it when the task is interactive or multi-step. For single-shot work prefer `/browserless:smart-scrape` (scrape, screenshot, pdf, links) instead.

Use only `mcp__plugin_browserless_browserless__browserless_agent` from the `plugin:browserless:browserless` server. Never substitute another Browserless connection: it may use a different account, region, or artifact mode. If this exact plugin tool is missing, stop and give the configuration guidance in **Auth** below. For a self-hosted request, explain that it is unsupported and ask before doing any work on hosted Browserless; do not offer or make REST calls as an alternative.

## Saving artifacts

For files to keep, use saved-download metadata; for an agent screenshot set `params.toDisk: true`. Inline screenshots are for intentional visual analysis and enter model context.

For a result marked `delivery: mcp-resource`, the saving path requires Claude Code CLI 2.1.327 or newer on Linux or macOS, an explicit `ReadMcpResourceTool` that saves binary resources to disk and returns only `blobSavedTo` metadata, and files up to 10 MiB. Use that tool with the `plugin:browserless:browserless` server and exact `resourceUri` returned by that server; never retrieve artifacts through another connection. Version alone and a visible resource-read tool do not prove safe handling: if the installed client is known to inline resource bytes or its disk-saving behavior is unknown, report unsupported saving before reading the resource. Disk saving was exercised on 2.1.327 on Linux and macOS; later versions must retain the same behavior.

Treat `blobSavedTo` as an opaque file to copy, never as content to inspect. Never use `Read`, `cat`, an image viewer, or any other open/read operation on that file or its copy to complete a save, even if copying fails. Check existence and byte count using filesystem metadata only, then copy to the user's destination and report that path only after the copy succeeds. The source is under Claude Code's sensitive `~/.claude` directory, so copying requires permission approval; explain that before attempting it. If permission is denied or unavailable (including headless runs), or the copy otherwise fails, stop the save workflow and report the failure and required approval. Do not bypass the denial, inspect the file, or switch tools to expose its contents.

A URI or handle is not a local file and does not authorize access: retrieval uses the configured MCP connection's authentication. Reads are single-use across MCP and HTTP, expire after 15 minutes, and may expire earlier when the session ends.

If the saving requirements are unmet, the saving tool is unavailable, the server returns legacy download instructions, or the file exceeds the native limit, report unsupported saving before reading the resource. Do not read credentials from files or the environment, ask for a token in chat, substitute a shell download, or bring base64/inline bytes into context. After a consumed transfer fails, report the failure; do not automatically rerun browser actions to regenerate the file.

## How to run it

Call the plugin's `mcp__plugin_browserless_browserless__browserless_agent` tool. It connects to a real Chromium session at `https://mcp.browserless.io`. Request a page **snapshot** (accessibility tree + element refs) explicitly; do not assume each action returns one.

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

All skills authenticate through the MCP connection using the plugin's options. Do not read local credentials or ask for a token in chat:

- **Browserless API token** (`browserless_token`): required. Claude Code stores it as a secret, not in `settings.json`, and sends it as the `Authorization` header.
- **Browserless API URL** (`api_url`): the hosted region, sent as `x-browserless-api-url`. Defaults to SFO (`https://production-sfo.browserless.io`). Use `https://production-lon.browserless.io`, `https://production-ams.browserless.io`, or another `https://*.browserless.io` URL such as a dedicated deployment. Arbitrary self-hosted URLs and self-hosted-only tokens are unsupported by this plugin; do not send those tokens to the hosted server or fall back to REST.

To set or change them, direct the user to `/plugin configure browserless@browserless` (or `browserless@inline` when the plugin is loaded with `--plugin-dir`), then restart Claude Code or reconnect Browserless in `/mcp` to apply them. Never print the token.

If `mcp__plugin_browserless_browserless__browserless_agent` isn't listed, the plugin's MCP connection is unavailable, even if another Browserless server is connected. Claude Code doesn't start the Browserless server until the required API token is set, so if the plugin server is missing from `/mcp`, run `/plugin configure browserless@browserless`, enter the token, and restart Claude Code or reconnect in `/mcp`.

If `/mcp` reports that the server rejected the configured Authorization header, the API URL option isn't a valid `https://*.browserless.io` URL. If Browserless connects but tool calls fail with `401: Invalid API key`, the token is wrong. Fix either with `/plugin configure browserless@browserless` and reconnect. Because the plugin always sends an `Authorization` header, Claude Code doesn't offer OAuth sign-in for this server.
