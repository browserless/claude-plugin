---
name: performance
description: Run a Lighthouse audit through Browserless MCP. Use when the user wants page-speed metrics, accessibility, SEO, best-practices scores, or a mobile or desktop performance audit.
---

# Performance

Call the `browserless_performance` MCP tool through the plugin's configured connection. The user's request is: "$ARGUMENTS"

If the tool is unavailable or authentication fails, stop tool work and tell the user to run `/plugin configure browserless@browserless` (`browserless@inline` for `--plugin-dir`), enter the hosted token in the sensitive configuration UI, then reconnect in `/mcp` or restart Claude Code. Do not probe or configure the connection through the shell, read local credentials, ask for a token in chat, invent MCP configuration, or fall back to REST authentication. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported; do not send those tokens to hosted MCP.

## Tool arguments

```json
{
  "url": "https://example.com",
  "categories": ["performance", "accessibility", "seo"],
  "device": "mobile"
}
```

Omit `categories` for all available categories. Supported categories are `performance`, `accessibility`, `best-practices`, `seo`, and `pwa`; report only scores the audit actually returns. `device` accepts `mobile` or `desktop`. Optional `config`, `budgets`, `timeout` in milliseconds, and `profile` depend on the connected tool's schema.

The tool returns a compact summary and may save the full JSON report outside the conversation. If it returns a pending widget and `auditRef`, let the widget finish: do not poll, call the app-only `browserless_performance_run`, claim scores, or start a replacement audit. For a later follow-up, use `browserless_performance_result` with the returned `auditRef` if that tool is available; if it is still pending, report that status rather than polling.

Before retrieving a saved report, read [the shared saving instructions](../agent/SKILL.md#saving-artifacts) and follow that workflow. Do not open the saved report merely to complete a save. Use the returned summary for analysis; do not fall back to shell authentication if report saving is unavailable.

Show category scores as percentages and highlight scores below 90%. Include available lab metrics such as FCP, LCP, TBT, CLS, and Speed Index with their units. This navigation audit does not measure INP; do not label TBT as INP.
