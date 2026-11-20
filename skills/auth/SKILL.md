---
name: auth
description: Configure the Browserless MCP connection. Use when the user wants to authenticate, change their hosted region, check connection status, or stop using the plugin's credentials.
disable-model-invocation: true
---

# Browserless Auth

All Browserless skills use only the `plugin:browserless:browserless` MCP server (`mcp__plugin_browserless_browserless__*`). Other Browserless connections do not establish this plugin's configuration or authentication status; never use them as substitutes. The user's request is: "$ARGUMENTS"

Claude Code collects the API token through the plugin's sensitive configuration option and sends it in the MCP Authorization header. Direct the user to the configuration UI; do not ask them to paste a token into conversation, read credentials from files or the environment, write a credential file, or make shell-authenticated requests.

## Setup or region

Tell the user to run `/plugin configure browserless@browserless` and enter their **Browserless API token** and **Browserless API URL**. For a plugin loaded with `--plugin-dir`, use `/plugin configure browserless@inline` instead. Then restart Claude Code or reconnect Browserless in `/mcp`.

Hosted regions are SFO (`https://production-sfo.browserless.io`, default), LON (`https://production-lon.browserless.io`), AMS (`https://production-ams.browserless.io`), or another hosted `https://*.browserless.io` URL. Arbitrary self-hosted endpoints and self-hosted-only tokens are unsupported by this plugin. For a self-hosted request, explain this limitation and ask before doing any work on hosted Browserless. Do not send a self-hosted token to the hosted server or offer or make REST calls as an alternative.

## Status

Direct the user to `/mcp` to inspect `plugin:browserless:browserless`, not a manually added server. Report only connection information actually available; a listed tool does not prove a token is valid. Never display a token or token prefix. Do not start a paid browser action solely to check authentication unless the user requests it.

If Browserless is missing, configure the required token and reconnect. If a tool returns `401: Invalid API key`, ask the user to replace the token through plugin configuration. If the server rejects the configured API URL, choose a hosted URL without credentials, query strings or fragments.

## Clear

Direct the user to `/plugin` to disable or uninstall Browserless to stop using its configured credentials. To replace credentials, use plugin configuration. Do not claim that disabling the plugin deletes stored credentials, old local files, or launch-environment values; this skill does not inspect or delete them.
