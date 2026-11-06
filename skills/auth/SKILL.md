---
name: auth
description: Configure Browserless API authentication. Set up your API token and region for all Browserless skills. Use when the user wants to authenticate, set their token, configure their API region, or check auth status.
disable-model-invocation: true
---

# Browserless Auth

Configure authentication for all Browserless API skills. The user's request is: "$ARGUMENTS"

## Subcommands

Based on `$ARGUMENTS`, do one of the following:

### If no arguments or "setup" — Interactive Setup

1. Ask the user for their Browserless API token. They can get one at https://www.browserless.io
2. Ask which API region they want to use:
   - **SFO** (US West, default): `https://production-sfo.browserless.io`
   - **LON** (London): `https://production-lon.browserless.io`
   - **AMS** (Amsterdam): `https://production-ams.browserless.io`
   - **Custom URL**: (prompt for the full API URL)
3. Create the config directory and write the config file:

```bash
mkdir -p ~/.browserless
cat > ~/.browserless/.env << 'ENVEOF'
BROWSERLESS_TOKEN=<their-token>
BROWSERLESS_API_URL=<their-chosen-url>
ENVEOF
chmod 600 ~/.browserless/.env
```

4. Validate the newly saved token and URL in a subshell, ignoring existing environment overrides for this setup check only:

```bash
(
unset BROWSERLESS_TOKEN BROWSERLESS_API_URL
_bl_token="${BROWSERLESS_TOKEN:-}"; _bl_url="${BROWSERLESS_API_URL:-}"
source ~/.browserless/.env 2>/dev/null
BROWSERLESS_TOKEN="${_bl_token:-${BROWSERLESS_TOKEN:-}}"
BROWSERLESS_API_URL="${_bl_url:-${BROWSERLESS_API_URL:-}}"
unset _bl_token _bl_url
curl -s -X POST "${BROWSERLESS_API_URL}/map?token=${BROWSERLESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "limit": 1}'
)
```

If the response contains `"success": true`, tell the user auth is configured and working. If it fails (401, 403, or connection error), tell them the token may be invalid and offer to retry.

5. Explain that both REST skills and the MCP agent can read the saved file. MCP uses the plugin's `headersHelper` (requires Python 3.9+) each time it connects. Use `/mcp` to **reconnect Browserless** after saving or changing credentials; no shell-profile block or new launch terminal is needed for saved credentials. Do not print the helper's output: it contains the token when configured. Do not claim MCP authentication or region is verified by the REST validation request.

The helper reads literal `KEY=value` assignments (shell-quoted values are supported), not shell commands or variable substitutions. Non-empty environment values take precedence independently when Claude Code passes them through. Current Claude Code filters token-like environment variables from plugin helpers, so use the saved file for reliable MCP token configuration. Existing environment overrides still apply to REST skills; remove stale overrides if the two disagree.

SFO/LON/AMS and other valid `browserless.io` URLs, including dedicated subdomains and trailing slashes, are passed through `x-browserless-api-url`. With no URL, MCP uses SFO. **Arbitrary self-hosted URLs remain REST-only**: the helper leaves them in the saved file but omits the MCP URL header and warns that hosted MCP uses SFO. A self-hosted-only token will not work on hosted Browserless. Clearly report this limitation for a self-hosted URL.

With no token, the helper omits `Authorization` entirely, allowing Claude Code's OAuth flow. An invalid configured token does not fall back to OAuth: correct or clear it, then reconnect in `/mcp`.

### If "status" — Check Current Config

Check if authentication is configured:

```bash
(
if [ -n "$BROWSERLESS_TOKEN" ]; then
  echo "Token set via environment variable"
  echo "Token: ${BROWSERLESS_TOKEN:0:8}..."
elif [ -f ~/.browserless/.env ]; then
  _bl_token="${BROWSERLESS_TOKEN:-}"; _bl_url="${BROWSERLESS_API_URL:-}"
  source ~/.browserless/.env 2>/dev/null
  BROWSERLESS_TOKEN="${_bl_token:-${BROWSERLESS_TOKEN:-}}"
  BROWSERLESS_API_URL="${_bl_url:-${BROWSERLESS_API_URL:-}}"
  unset _bl_token _bl_url
  echo "Token loaded from ~/.browserless/.env"
  echo "Token: ${BROWSERLESS_TOKEN:0:8}..."
  echo "API URL: ${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}"
else
  echo "Not configured"
fi
)
```

Report the status to the user. If configured, show the first 8 characters of the token (masked) and the API URL. If not configured, suggest running `/browserless:auth` to set up.

This checks REST credentials, not the active MCP connection. Use `/mcp` to inspect or reconnect Browserless; the helper reloads the saved file on reconnect. Do not run the helper to display status, since its JSON output may contain the full token.

### If "clear" — Remove Saved Credentials

Remove the saved config:

```bash
rm -f ~/.browserless/.env
echo "Browserless credentials removed."
```

Confirm that the saved file has been removed, but explain that existing environment exports and the active MCP connection are not cleared by deleting it. Reconnect Browserless in `/mcp` to reload credentials. If the helper still receives an environment token, remove that override from the launch environment and restart Claude Code; changing an export in a subprocess cannot change its parent. Clear existing OAuth authentication separately in `/mcp` if the user also wants to sign out. With neither a saved nor a visible environment token, the helper omits `Authorization`, allowing OAuth sign-in.

### If "region" — Change Region Only

Update just the API URL in the existing config:

1. Ask which region (SFO, LON, AMS, or custom URL)
2. Update the `BROWSERLESS_API_URL` line in `~/.browserless/.env`
3. Reconnect Browserless in `/mcp` so the helper reads the new URL. Explain that non-empty visible environment URL overrides take precedence, `browserless.io` URLs work with hosted MCP, and arbitrary self-hosted URLs remain REST-only (MCP uses SFO with a warning).
