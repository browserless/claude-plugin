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

5. Explain that saving the file configures REST skills only. The MCP agent reads the environment inherited by Claude Code at startup, not this file. Instruct the user to add the following block **once** to the startup file for the shell they use to launch Claude Code (`~/.zshrc` for zsh; `~/.bashrc` for interactive bash, or `~/.bash_profile` if they launch from a login shell). Do not edit their shell profile without permission, and do not print their token:

```bash
if [ -f "$HOME/.browserless/.env" ]; then
  source "$HOME/.browserless/.env"
  export BROWSERLESS_TOKEN
  case "${BROWSERLESS_API_URL:-}" in
    https://production-sfo.browserless.io|https://production-lon.browserless.io|https://production-ams.browserless.io)
      export BROWSERLESS_API_URL ;;
    *)
      unset BROWSERLESS_API_URL ;;
  esac
fi
```

Tell the user to **open a new terminal, then fully quit and restart Claude Code from that terminal**. Exporting in a skill's subprocess cannot update the running Claude Code process. After restart, use `/mcp` to check the Browserless connection before trying `/browserless:agent`.

For SFO/LON/AMS, the exported URL applies to both REST skills and agent sessions through the `x-browserless-api-url` MCP header. An unset URL defaults MCP to SFO; an explicitly empty URL does not use Claude Code's default, so unset it rather than exporting an empty string.

**Custom URLs are REST-skills-only with the hosted MCP server.** The block intentionally leaves custom URLs in the saved file and unsets the environment URL: REST skills load the saved custom URL, while MCP uses SFO. The saved token is still exported to MCP and must be valid for hosted Browserless; a self-hosted-only token will not work there. Clearly report this limitation when the user chooses a custom URL. Do not claim MCP authentication or region is verified by the REST validation request.

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

This checks REST credentials, not the parent Claude Code process's MCP configuration. Remind the user that saved credentials require the shell-profile export block and a Claude Code restart for MCP; use `/mcp` to inspect the actual connection.

### If "clear" — Remove Saved Credentials

Remove the saved config:

```bash
rm -f ~/.browserless/.env
echo "Browserless credentials removed."
```

Confirm that the saved file has been removed, but explain that existing environment exports and the running MCP connection are not cleared by deleting it. Instruct the user to remove any explicit Browserless exports from their shell profile, run `unset BROWSERLESS_TOKEN BROWSERLESS_API_URL` in their launch terminal, and fully quit and restart Claude Code. With no token, the hosted MCP server offers OAuth sign-in.

### If "region" — Change Region Only

Update just the API URL in the existing config:

1. Ask which region (SFO, LON, AMS, or custom URL)
2. Update the `BROWSERLESS_API_URL` line in `~/.browserless/.env`
3. If the shell-profile block above is not installed, provide it. Tell the user to open a new terminal and fully quit and restart Claude Code so MCP receives the new region. Explain that custom URLs remain REST-only; the hosted MCP agent uses SFO with the block above.
