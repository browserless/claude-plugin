---
name: smart-scrape
description: Scrape one webpage through Browserless MCP. Use when the user wants page text, HTML, links, structured extraction, a summary, a screenshot, or a PDF; use crawl for content across many pages.
---

# Smart Scrape

Call only `mcp__plugin_browserless_browserless__browserless_smartscraper` from the `plugin:browserless:browserless` server. Never substitute a same-named tool on another server: it may use a different account, region, or artifact mode. The user's request is: "$ARGUMENTS"

If this exact plugin tool is missing, stop and give the configuration guidance below, even if another Browserless connection is available. For a self-hosted request, explain that it is unsupported and ask before doing any work on hosted Browserless; do not offer or make REST calls as an alternative.

If the tool is unavailable or authentication fails, stop tool work and tell the user to run `/plugin configure browserless@browserless` (`browserless@inline` for `--plugin-dir`), enter the hosted token in the sensitive configuration UI, then reconnect in `/mcp` or restart Claude Code. Do not probe or configure the connection through the shell, read local credentials, ask for a token in chat, invent MCP configuration, or fall back to REST authentication. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported; do not send those tokens to hosted MCP.

## Tool arguments

```json
{
  "url": "https://example.com",
  "formats": ["markdown"]
}
```

Default to `markdown` for reading or summarizing a page. Request only the formats needed: `markdown`, `html`, `rawText`, `links`, `screenshot`, `pdf`, `json`, or `summary`. The AI `json` and `summary` formats add extraction units. For `json`, supply `jsonOptions.schema`, `jsonOptions.prompt`, or both; do not supply `jsonOptions` for other formats.

Optional arguments include `timeout`, `profile`, `onlyMainContent`, `includeTags`, `excludeTags`, `headers`, and `waitFor`. `waitFor` is milliseconds, from 0 to 30000. Do not combine `includeTags` with `excludeTags` or `onlyMainContent`. Use only the connected tool's supported parameters; authentication to Browserless comes from the MCP connection, not target-page headers.

For screenshots or PDFs to keep, set `toDisk: true`. This saves binary attachments, not requested text extraction. Before retrieving a saved artifact, read [the shared saving instructions](../agent/SKILL.md#saving-artifacts) and follow that workflow. Do not open the saved file as a save fallback. If the user explicitly wants inline image analysis, `toDisk: false` permits it and the image enters model context.

Present the requested content and any extraction warnings. A successful page fetch does not imply that every requested format was produced. For content across multiple pages, use `/browserless:crawl` instead.
