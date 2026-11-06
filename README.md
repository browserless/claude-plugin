# Browserless Plugin for Claude Code

A Claude Code plugin that gives Claude direct access to the [Browserless.io](https://docs.browserless.io/rest-apis/intro) REST APIs: scrape webpages, take screenshots, generate PDFs, search the web, map site structures, and run custom browser automation, all from natural language.

## Installation

Install from inside Claude Code:

```
/plugin marketplace add browserless/claude-plugin
/plugin install browserless@browserless
```

To pull future updates:

```
/plugin marketplace update browserless
```

### Manual install (local development)

Clone the repo and point Claude Code at the plugin directory:

```bash
git clone https://github.com/browserless/claude-plugin.git
cd claude-plugin
claude --plugin-dir .
```

## Setup

### 1. Get a Browserless API token

Sign up for free at [browserless.io](https://www.browserless.io) and grab your API token.

### 2. Authenticate

Run the auth skill inside Claude Code:

```
/browserless:auth
```

This prompts for your token and preferred API region (SFO, LON, AMS, or a custom URL), then saves credentials to `~/.browserless/.env`. Both REST skills and the MCP agent read the saved file. After setup, reconnect Browserless in `/mcp` to reload credentials; no shell-profile block or new launch terminal is needed. The MCP header helper requires **Python 3.9+** on `PATH` as `python3`.

Environment variables can override saved REST credentials:

```bash
export BROWSERLESS_TOKEN=your-token-here
export BROWSERLESS_API_URL=https://production-lon.browserless.io
```

The MCP helper also honors non-empty environment values when Claude Code passes them through. Current Claude Code [filters token-like environment variables from plugin helpers](https://code.claude.com/docs/en/mcp#which-variables-a-helper-can-read), including `BROWSERLESS_TOKEN`, so use `/browserless:auth` and the saved file for reliable MCP authentication. Changing an inherited environment override still requires restarting Claude Code, but changing the saved file only requires reconnecting. Arbitrary self-hosted URLs remain REST-only; see [API Regions](#api-regions).

### 3. Start using skills

Once authenticated, all skills are available as slash commands:

```
/browserless:smart-scrape https://example.com
/browserless:agent log into https://example.com and download my latest invoice
/browserless:search what is browserless
/browserless:map https://example.com
/browserless:function click the login button on https://example.com
/browserless:export save https://example.com with all assets for offline viewing
/browserless:performance run a lighthouse audit on https://example.com
/browserless:crawl crawl https://example.com up to 3 levels deep
```

## Skills

| Skill | Command | Description | Example Prompt |
|-------|---------|-------------|----------------|
| **Auth** | `/browserless:auth` | Configure API token and region. Subcommands: `status`, `clear`, `region`. | |
| **Agent** | `/browserless:agent` | Interactive, stateful browser session (via the MCP server) — navigate, click, type, log in, handle captchas/cookie banners, multi-step flows, file up/downloads. | `log into https://example.com and download my latest invoice` |
| **Smart Scrape** | `/browserless:smart-scrape` | Scrape webpages with cascading strategies (HTTP fetch, proxy, headless browser, captcha solving). Returns markdown, HTML, screenshots, PDFs, or links. | `summarize the main content of https://news.ycombinator.com` |
| **Search** | `/browserless:search` | Search the web and optionally scrape result pages. Supports web, news, and image sources with time-based filtering and content categories. | `find recent AI news en español from the last week` |
| **Map** | `/browserless:map` | Discover and list all URLs on a website. Crawls sitemaps, pages, and subdomains with relevance-based search filtering. | `save a list of all URLs on https://browserless.io in json format` |
| **Function** | `/browserless:function` | Execute custom Puppeteer JavaScript in a cloud browser. Run arbitrary automation scripts, interact with page elements, fill forms, and return structured data. | `load the ./scripts/sample-script.js file and run it using /function` |
| **Export** | `/browserless:export` | Export a webpage in its native format, optionally bundling all resources (CSS, JS, images) into a ZIP archive for offline use. | `save https://example.com with all assets as a ZIP` |
| **Performance** | `/browserless:performance` | Run a Lighthouse audit on a webpage. Get scores for performance, accessibility, best practices, SEO, and PWA. | `audit the performance and accessibility of https://example.com` |
| **Crawl** | `/browserless:crawl` | Crawl an entire website starting from a seed URL, following links to configurable depth while scraping all discovered pages. | `crawl https://docs.browserless.io up to 3 levels deep` |

> Screenshots, PDFs, and file downloads no longer have standalone skills — they're covered by `/browserless:smart-scrape` (screenshot/pdf via output formats) and `/browserless:agent` (downloads during a flow).


## MCP Server (browser agent + tools)

Installing this plugin also registers the hosted **Browserless MCP server** (`https://mcp.browserless.io/mcp`), which adds tools the REST skills don't cover — most notably `browserless_agent`, an interactive browser-automation agent (navigate, click, type, snapshot, solve captchas, handle logins) that holds a live session across calls.

MCP uses [`headersHelper`](https://code.claude.com/docs/en/mcp#use-dynamic-headers-for-custom-authentication) to run `scripts/mcp-headers.py` at each connection. It reads saved `BROWSERLESS_TOKEN` and `BROWSERLESS_API_URL` from `~/.browserless/.env`, with non-empty visible environment values taking precedence independently. It sends supported hosted URLs through `x-browserless-api-url`; without an override, the server defaults to SFO. Reconnect Browserless from `/mcp` after changing saved credentials or region. Never display the helper's output: its JSON may contain the full token.

With no token, the helper omits `Authorization` entirely, allowing Claude Code's OAuth sign-in flow. A static `Authorization` header would disable that flow, even if empty, so none is configured. An invalid configured token does not fall back to OAuth; correct or clear it and reconnect. The interactive sign-in flow still requires validation in a live Claude Code session.

**Troubleshooting:** “Needs authentication” does not prove the saved token is absent. Claude Code can also drop the helper's headers after a failure, such as missing `python3`, Python older than 3.9, malformed `.env` quoting, or an invalid URL. Check helper stderr and `python3 --version`, correct the saved assignments, then reconnect in `/mcp`. The helper reports failures without credential contents or tracebacks. Do not print its stdout: successful output can contain the full token.

| Tool | Description |
|------|-------------|
| `browserless_agent` | Interactive browser session — navigate, snapshot, click, type, multi-step automation |
| `browserless_smartscraper` | Scrape a page (markdown/HTML/screenshot/PDF/links) |
| `browserless_crawl` | Crawl a site to configurable depth |
| `browserless_map` | Discover all URLs on a site |
| `browserless_search` | Web/news/image search |
| `browserless_function` | Run custom Puppeteer code |
| `browserless_export` | Export a page with all assets |
| `browserless_performance` | Lighthouse audit |

## Auth Management

| Command | Description |
|---------|-------------|
| `/browserless:auth` | Interactive setup — set token and region |
| `/browserless:auth status` | Check if authentication is configured |
| `/browserless:auth clear` | Remove saved credentials |
| `/browserless:auth region` | Change API region without re-entering token |

Credentials are stored in `~/.browserless/.env` with `600` permissions. For REST skills, the token resolution order is:

1. `BROWSERLESS_TOKEN` environment variable (if non-empty in the shell)
2. `~/.browserless/.env` file (written by `/browserless:auth`)
3. If neither provides a non-empty token, ask the user to run `/browserless:auth`.

`BROWSERLESS_API_URL` follows the same precedence independently: a non-empty environment variable wins over the saved URL. If neither provides a URL, REST requests default to `https://production-sfo.browserless.io`. Empty environment values use the saved fallback. Loading saved credentials does not change the file.

REST examples load credentials and make requests inside a subshell. Saved values do not persist in the calling shell, so later calls pick up changes to the saved token or region while preserving environment overrides.

During `/browserless:auth` setup, the validation request checks the newly saved token and URL, ignoring environment overrides for that check only. Subsequent REST requests still prefer the environment.

For MCP, the helper reloads the saved file on reconnect, without executing it as a shell script. Store literal `KEY=value` assignments; shell-quoted values are supported, shell commands and variable substitutions are not evaluated. Use the saved file because Claude Code may remove credential variables from the helper's environment. REST validation and `/browserless:auth status` do not verify the MCP connection—use `/mcp` for that.

`/browserless:auth clear` removes the saved file only. Reconnect in `/mcp` to reload headers. Existing visible environment overrides require removing the override and restarting Claude Code. Existing OAuth authentication must be cleared separately in `/mcp` to sign out.

## API Regions

| Region | URL | Supported by |
|--------|-----|--------------|
| SFO (US West, default) | `https://production-sfo.browserless.io` | REST skills and hosted MCP |
| LON (London) | `https://production-lon.browserless.io` | REST skills and hosted MCP |
| AMS (Amsterdam) | `https://production-ams.browserless.io` | REST skills and hosted MCP |
| Other hosted | Valid `browserless.io` URLs, including `https://chrome.browserless.io` and dedicated subdomains | REST skills and hosted MCP |
| Self-hosted | Arbitrary non-Browserless URLs | REST skills only |

The helper strips trailing slashes from supported hosted URLs before forwarding them, so REST-backed MCP tools do not construct double-slash paths. Hosted URLs must use **HTTPS**, without credentials, query strings or fragments. Arbitrary self-hosted URLs stay in the saved file for REST; the helper omits that URL header and warns that hosted MCP will use SFO. A self-hosted-only token will not authenticate to hosted Browserless. The helper's no-token flow sends no empty Bearer header and does not depend on the server's empty-Bearer fix being released first.

## Plugin Structure

```
.claude-plugin/
  plugin.json           # Plugin metadata
.mcp.json               # Hosted Browserless MCP server (adds browserless_agent + tools)
hooks/
  hooks.json            # SessionStart hook config
scripts/
  check-auth.sh         # Warns if token is not configured
  mcp-headers.py        # Dynamic MCP headers from saved credentials (Python 3.9+)
skills/
  auth/SKILL.md         # Authentication setup
  agent/SKILL.md        # Interactive browser session (MCP-backed)
  smart-scrape/SKILL.md # Web scraping (incl. screenshot/pdf via formats)
  search/SKILL.md       # Web search
  map/SKILL.md          # URL discovery
  function/SKILL.md     # Custom Puppeteer code
  export/SKILL.md       # Webpage export with resources
  performance/SKILL.md  # Lighthouse audits
  crawl/SKILL.md        # Multi-page website crawling
```

## API Reference

Most skills map to a Browserless REST API endpoint; `agent` is served by the bundled MCP server over a WebSocket session instead. Full API documentation is available at [docs.browserless.io/rest-apis/intro](https://docs.browserless.io/rest-apis/intro).

| Skill | Endpoint |
|-------|----------|
| Agent | MCP `browserless_agent` (WebSocket `/chromium/agent`) |
| Smart Scrape | `POST /smart-scrape` |
| Search | `POST /search` |
| Map | `POST /map` |
| Function | `POST /function` |
| Export | `POST /export` |
| Performance | `POST /performance` |
| Crawl | `POST /crawl` |

## Tests

Run `python3 scripts/test-credentials.py` with bash and zsh installed. It executes the documented REST snippets and the configured MCP header helper with a temporary home directory and no network requests.

## License

SSPL-1.0
