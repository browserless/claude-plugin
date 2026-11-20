---
name: function
description: Run custom Puppeteer JavaScript through Browserless MCP. Use when the user needs a fixed browser automation script, custom extraction, form interaction, or structured results beyond a simple scrape.
---

# Function

Call the `browserless_function` MCP tool through the plugin's configured connection. The user's request is: "$ARGUMENTS"

If the tool is unavailable or authentication fails, stop tool work and tell the user to run `/plugin configure browserless@browserless` (`browserless@inline` for `--plugin-dir`), enter the hosted token in the sensitive configuration UI, then reconnect in `/mcp` or restart Claude Code. Do not probe or configure the connection through the shell, read local credentials, ask for a token in chat, invent MCP configuration, or fall back to REST authentication. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported; do not send those tokens to hosted MCP.

## Tool arguments

```json
{
  "code": "export default async ({ page, context }) => { await page.goto(context.url); return { title: await page.title() }; };",
  "context": { "url": "https://example.com" }
}
```

`code` is an ESM module whose default export receives `{ page, context }`. Pass dynamic inputs in the optional `context` object. Use the optional `timeout` in milliseconds and `profile` only when needed and supported by the connected tool.

Return the result directly: a string becomes text, an object or array becomes JSON, and raw bytes from `page.screenshot()` or `page.pdf()` become a binary result. Do not wrap bytes in `{ data, type }`, encode them as base64, or use `Buffer`, which is unavailable inside the function. Filter large extracted datasets inside the function rather than returning unnecessary content. Text results are capped at 200,000 characters.

For a file to keep, set `toDisk: true`, including for JSON or text. For intentional inline binary analysis, use `toDisk: false` only when that is the user's intent. Before retrieving a saved artifact, read [the shared saving instructions](../agent/SKILL.md#saving-artifacts) and follow that workflow. If safe saving is unsupported, report the limitation instead of downloading through the shell or reading saved bytes into context.

Write the script for the user's requested actions, wait for selectors or navigation where needed, and report the returned result. For an interactive session that must persist across calls, use `/browserless:agent` instead.
