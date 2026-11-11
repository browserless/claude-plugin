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

5. Explain that the saved file is used by the REST skills only. The MCP agent (`/browserless:agent`) reads the plugin's own options instead, which this skill can't set. Tell the user to run `/plugin configure browserless@browserless` and enter:
   - **Browserless API token**: the same token. Claude Code stores it in the system's secure credential store.
   - **Browserless API URL**: the same region URL, if it's a hosted `https://*.browserless.io` URL. For a self-hosted URL, keep the default there, because the hosted MCP server rejects self-hosted URLs and a self-hosted-only token doesn't work on hosted Browserless. Clearly report this limitation for a self-hosted URL.

   Then restart Claude Code, or reconnect Browserless in `/mcp` if it's already listed. Do not claim MCP authentication or region is verified by the REST validation request.

Existing environment overrides still apply to REST skills; remove stale overrides if they disagree with the saved file.

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

This checks REST credentials, not the MCP connection. The MCP agent uses the plugin's options instead: use `/mcp` to see whether Browserless is connected, and `/plugin configure browserless@browserless` to review or change its token and API URL.

### If "clear" — Remove Saved Credentials

Remove the saved config:

```bash
rm -f ~/.browserless/.env
echo "Browserless credentials removed."
```

Confirm that the saved file has been removed, but explain that it only affects the REST skills. Existing environment exports still apply to REST skills; remove them from the launch environment and restart Claude Code if needed, because changing an export in a subprocess cannot change its parent. The MCP agent's token is a plugin option and isn't removed by this: replace it with `/plugin configure browserless@browserless`, or disable the plugin in `/plugin` to stop using it.

### If "region" — Change Region Only

Update just the API URL in the existing config:

1. Ask which region (SFO, LON, AMS, or custom URL)
2. Update the `BROWSERLESS_API_URL` line in `~/.browserless/.env`
3. For the MCP agent, tell the user to set the same URL as the **Browserless API URL** option, either in `/plugin configure browserless@browserless` or in the plugin's row in `/config`, then restart Claude Code or reconnect Browserless in `/mcp`. Explain that non-empty environment URL overrides still take precedence for REST skills, `https://*.browserless.io` URLs work with hosted MCP, and self-hosted URLs work with REST skills only: keep the MCP option on a hosted region for those.
