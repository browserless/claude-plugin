---
name: search
description: Search the web through Browserless MCP. Use when the user wants web, news, or image search results, recent information, language filtering, or optional result-page scraping.
---

# Search

Call the `browserless_search` MCP tool through the plugin's configured connection. The user's request is: "$ARGUMENTS"

If the tool is unavailable or authentication fails, stop tool work and tell the user to run `/plugin configure browserless@browserless` (`browserless@inline` for `--plugin-dir`), enter the hosted token in the sensitive configuration UI, then reconnect in `/mcp` or restart Claude Code. Do not probe or configure the connection through the shell, read local credentials, ask for a token in chat, invent MCP configuration, or fall back to REST authentication. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported; do not send those tokens to hosted MCP.

## Tool arguments

```json
{
  "query": "browserless headless browser",
  "sources": ["web"],
  "limit": 10,
  "lang": "en"
}
```

`sources` accepts `web`, `news`, and `images`. Use `tbs` for `day`, `week`, `month`, or `year`; `categories` for `github`, `pdf`, or `research`. Optional arguments include `country`, `location`, and `timeout` in milliseconds. The maximum `limit` is 100.

When the user requests scraping of result pages and the connected tool exposes it, set `scrapeOptions.formats` to the needed formats (`markdown`, `html`, `links`, or `screenshot`). Supported shaping options are `onlyMainContent`, `includeTags`, and `excludeTags`. Do not add REST-only options or assume every MCP surface supports result-page scraping.

Present search results with their source URLs. For a specific page's content, use `/browserless:smart-scrape`. For a screenshot the user wants to keep, use that skill's saved-artifact path rather than treating search output as a local file.
