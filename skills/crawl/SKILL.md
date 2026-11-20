---
name: crawl
description: Crawl a website through Browserless MCP to extract content from multiple pages. Use when the user wants site-wide scraping, link-following to a chosen depth, or content from many pages.
---

# Crawl

Call the `browserless_crawl` MCP tool through the plugin's configured connection. The user's request is: "$ARGUMENTS"

If the tool is unavailable or authentication fails, stop tool work and tell the user to run `/plugin configure browserless@browserless` (`browserless@inline` for `--plugin-dir`), enter the hosted token in the sensitive configuration UI, then reconnect in `/mcp` or restart Claude Code. Do not probe or configure the connection through the shell, read local credentials, ask for a token in chat, invent MCP configuration, or fall back to REST authentication. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported; do not send those tokens to hosted MCP.

## Tool arguments

```json
{
  "url": "https://example.com",
  "limit": 50,
  "maxDepth": 3,
  "scrapeOptions": { "formats": ["markdown"], "onlyMainContent": true },
  "waitForCompletion": true
}
```

The server starts the crawl, polls, retrieves results and fetches page content when `waitForCompletion` is true (the default). Do not reproduce that loop with curl. Bound the crawl to the user's requested scope using `limit`, `maxDepth`, `allowExternalLinks`, `allowSubdomains`, `includePaths`, and `excludePaths`. `sitemap` accepts `auto`, `force`, or `skip`. Other supported options include `maxRetries`, `delay`, `timeout`, and `profile`.

`scrapeOptions.formats` accepts `markdown`, `html`, or `rawText`. Supported scrape options include `onlyMainContent`, `includeTags`, `excludeTags`, `waitFor`, `headers`, and `timeout`. Timing values are in milliseconds. Use `pollInterval` and `maxWaitTime` to control server-side waiting when needed.

Prefer `waitForCompletion: true` when the user expects results. With false, the tool returns a crawl ID immediately, but the current MCP tool does not expose listing, cancellation, or resuming/status-checking an existing crawl. If asked for one of those operations, or if waiting times out, report the limitation and any returned ID; do not invent an operation parameter, restart the crawl automatically, or read local credentials to poll REST. Webhook configuration is not exposed by this tool.

Summarize completion status, page counts, failures and returned content. Results may be truncated: the server fetches full content for at most 50 completed pages and caps each page's displayed content. Do not claim that the returned text is a complete archive of the crawl. For URL discovery without page content, use `/browserless:map`.
