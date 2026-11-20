---
name: map
description: Discover URLs on a website through Browserless MCP. Use when the user wants a sitemap, a website's structure, all pages on a site, or URLs ranked by relevance.
---

# Map

Call only `mcp__plugin_browserless_browserless__browserless_map` from the `plugin:browserless:browserless` server. Never substitute a same-named tool on another server: it may use a different account, region, or artifact mode. The user's request is: "$ARGUMENTS"

If this exact plugin tool is missing, stop and give the configuration guidance below, even if another Browserless connection is available. For a self-hosted request, explain that it is unsupported and ask before doing any work on hosted Browserless; do not offer or make REST calls as an alternative.

If the tool is unavailable or authentication fails, stop tool work and tell the user to run `/plugin configure browserless@browserless` (`browserless@inline` for `--plugin-dir`), enter the hosted token in the sensitive configuration UI, then reconnect in `/mcp` or restart Claude Code. Do not probe or configure the connection through the shell, read local credentials, ask for a token in chat, invent MCP configuration, or fall back to REST authentication. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported; do not send those tokens to hosted MCP.

## Tool arguments

```json
{
  "url": "https://example.com",
  "limit": 100,
  "sitemap": "include"
}
```

Use `search` to rank URLs by relevance. `sitemap` accepts `include`, `skip`, or `only`. Optional `includeSubdomains` and `ignoreQueryParameters` default to true. `limit` defaults to 100, with a maximum of 5000 on the full endpoint; follow the connected tool's schema if it has a lower limit. `timeout` is in milliseconds. Pass supported options as tool arguments, not query parameters or a REST request body. The MCP tool does not expose the REST `location` option.

Present the returned URLs, titles and descriptions in a readable list. Distinguish an empty result from a failed request. If the user wants page content rather than URL discovery, use `/browserless:smart-scrape` or `/browserless:crawl`.
