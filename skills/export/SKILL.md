---
name: export
description: Save a webpage or file through Browserless MCP, optionally bundling page assets into a ZIP. Use when the user wants an offline copy, a native-format download, or a page with its resources.
---

# Export

Call only `mcp__plugin_browserless_browserless__browserless_export` from the `plugin:browserless:browserless` server. Never substitute a same-named tool on another server: it may use a different account, region, or artifact mode. The user's request is: "$ARGUMENTS"

If this exact plugin tool is missing, stop and give the configuration guidance below, even if another Browserless connection is available. For a self-hosted request, explain that it is unsupported and ask before doing any work on hosted Browserless; do not offer or make REST calls as an alternative.

If the tool is unavailable or authentication fails, stop tool work and tell the user to run `/plugin configure browserless@browserless` (`browserless@inline` for `--plugin-dir`), enter the hosted token in the sensitive configuration UI, then reconnect in `/mcp` or restart Claude Code. Do not probe or configure the connection through the shell, read local credentials, ask for a token in chat, invent MCP configuration, or fall back to REST authentication. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported; do not send those tokens to hosted MCP.

## Tool arguments

```json
{
  "url": "https://example.com",
  "includeResources": true,
  "toDisk": true
}
```

Use `toDisk: true` for files to keep, including exported HTML. Set `includeResources: true` only when the user wants all page assets bundled into a ZIP; otherwise omit it or set false. Optional arguments include `gotoOptions.waitUntil`, `gotoOptions.timeout`, `bestAttempt`, `waitForTimeout`, `timeout`, and `profile`. Follow the connected tool's schema; not every endpoint exposes bundling or saved-file options. Do not send unsupported REST-only wait options.

Before retrieving any saved artifact, read [the shared saving instructions](../agent/SKILL.md#saving-artifacts) and follow that workflow. A returned resource URI is not a local path. Copy only through the verified resource-to-disk path, obtain permission for the copy, and report the destination only after success. If safe saving is unavailable, stop and report it; do not inspect saved bytes or use shell-download instructions as a fallback.

Use the returned MIME type and filename when choosing the destination extension. Do not claim an export saved locally merely because the tool returned download metadata.
