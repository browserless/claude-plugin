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

A plugin loaded with `--plugin-dir` has the id `browserless@inline`, so set its options with `/plugin configure browserless@inline` instead of `browserless@browserless`.

## Setup

### 1. Get a Browserless API token

Sign up for free at [browserless.io](https://www.browserless.io) and copy your API token from your [account dashboard](https://www.browserless.io/account/home).

### 2. Configure the plugin

When you install or enable the plugin in `/plugin`, Claude Code asks for two plugin options:

- **Browserless API token** (required): used by the hosted MCP server, which powers `/browserless:agent`. Claude Code stores it with its own credentials, never in `settings.json`: in the macOS Keychain on macOS, and in Claude Code's `.credentials.json` file (readable only by your user) on Linux and Windows.
- **Browserless API URL**: the hosted region the MCP server uses. Defaults to `https://production-sfo.browserless.io`. See [API Regions](#api-regions).

To change them later, run `/plugin configure browserless@browserless`, then restart Claude Code or reconnect Browserless in `/mcp` to apply them. If you install from a shell with `claude plugin install`, pass the values with `--config KEY=VALUE`, or pipe a JSON object to `claude plugin configure browserless@browserless --values-stdin` afterward.

### 3. Authenticate the REST skills

The REST skills (smart scrape, search, map, function, export, performance and crawl) call the Browserless REST APIs directly. Run the auth skill inside Claude Code:

```
/browserless:auth
```

This prompts for your token and preferred API region (SFO, LON, AMS, or a custom URL), then saves credentials to `~/.browserless/.env` for the REST skills.

Environment variables can override saved REST credentials:

```bash
export BROWSERLESS_TOKEN=your-token-here
export BROWSERLESS_API_URL=https://production-lon.browserless.io
```

### Upgrading from 1.0.0

Version 1.1.0 no longer reads `~/.browserless/.env` for the MCP server, and drops the session-start reminder. Until you set the new API token option, Browserless doesn't appear in `/mcp` and `/browserless:agent` can't run. After updating, run `/plugin configure browserless@browserless` once, enter your API token and region, then restart Claude Code. The REST skills keep using your saved `~/.browserless/.env` and environment variables as before.

### 4. Start using skills

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
| **Function** | `/browserless:function` | Execute custom Puppeteer JavaScript in a cloud browser. Run arbitrary automation scripts, interact with page elements, fill forms, and return structured data. | `go to https://example.com and return the page title and all link texts as JSON` |
| **Export** | `/browserless:export` | Export a webpage in its native format, optionally bundling all resources (CSS, JS, images) into a ZIP archive for offline use. | `save https://example.com with all assets as a ZIP` |
| **Performance** | `/browserless:performance` | Run a Lighthouse audit on a webpage. Get scores for performance, accessibility, best practices, SEO, and PWA. | `audit the performance and accessibility of https://example.com` |
| **Crawl** | `/browserless:crawl` | Crawl an entire website starting from a seed URL, following links to configurable depth while scraping all discovered pages. | `crawl https://docs.browserless.io up to 3 levels deep` |

> Screenshots, PDFs, and file downloads no longer have standalone skills — they're covered by `/browserless:smart-scrape` (screenshot/pdf via output formats) and `/browserless:agent` (downloads during a flow).


## MCP Server (browser agent + tools)

Installing this plugin also registers the hosted **Browserless MCP server** (`https://mcp.browserless.io/mcp`), which adds tools the REST skills don't cover — most notably `browserless_agent`, an interactive browser-automation agent (navigate, click, type, snapshot, solve captchas, handle logins) that holds a live session across calls.

The MCP server authenticates with the plugin's options. Claude Code sends the **Browserless API token** as the `Authorization` header and the **Browserless API URL** as `x-browserless-api-url`. The plugin runs no local scripts or helpers. Because an `Authorization` header is always configured, Claude Code doesn't offer OAuth sign-in for this server: set the token instead.

**Troubleshooting:**

- **Browserless is missing from `/mcp`:** Claude Code doesn't start the server until the required API token is set. Run `/plugin configure browserless@browserless`, enter the token, then restart Claude Code.
- **`/mcp` reports that the server rejected the configured Authorization header:** the **Browserless API URL** option isn't a valid `https://*.browserless.io` URL. Claude Code names the header, but the server refused the URL. Fix it with `/plugin configure browserless@browserless` and reconnect Browserless in `/mcp`.
- **Browserless connects, but tool calls fail with `401: Invalid API key`:** the API token is wrong. The server checks the token on each tool call, not when connecting. Replace it with `/plugin configure browserless@browserless` and reconnect.

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
| `/browserless:auth` | Interactive setup — set token and region for REST skills |
| `/browserless:auth status` | Check if REST authentication is configured |
| `/browserless:auth clear` | Remove saved REST credentials |
| `/browserless:auth region` | Change the REST API region without re-entering the token |
| `/plugin configure browserless@browserless` | Set the MCP server's token and API URL |

REST credentials are stored in `~/.browserless/.env` with `600` permissions. For REST skills, the token resolution order is:

1. `BROWSERLESS_TOKEN` environment variable (if non-empty in the shell)
2. `~/.browserless/.env` file (written by `/browserless:auth`)
3. If neither provides a non-empty token, ask the user to run `/browserless:auth`.

`BROWSERLESS_API_URL` follows the same precedence independently: a non-empty environment variable wins over the saved URL. If neither provides a URL, REST requests default to `https://production-sfo.browserless.io`. Empty environment values use the saved fallback. Loading saved credentials does not change the file.

REST examples load credentials and make requests inside a subshell. Saved values do not persist in the calling shell, so later calls pick up changes to the saved token or region while preserving environment overrides.

During `/browserless:auth` setup, the validation request checks the newly saved token and URL, ignoring environment overrides for that check only. Subsequent REST requests still prefer the environment.

The MCP server doesn't read `~/.browserless/.env` or environment variables. It uses the plugin options set with `/plugin configure browserless@browserless`. REST validation and `/browserless:auth status` do not verify the MCP connection—use `/mcp` for that. `/browserless:auth clear` removes the saved REST file only.

## API Regions

| Region | URL | Supported by |
|--------|-----|--------------|
| SFO (US West, default) | `https://production-sfo.browserless.io` | REST skills and hosted MCP |
| LON (London) | `https://production-lon.browserless.io` | REST skills and hosted MCP |
| AMS (Amsterdam) | `https://production-ams.browserless.io` | REST skills and hosted MCP |
| Other hosted | Valid `browserless.io` URLs, including `https://chrome.browserless.io` and dedicated subdomains | REST skills and hosted MCP |
| Self-hosted | Arbitrary non-Browserless URLs | REST skills only |

Set the REST region with `/browserless:auth region` and the MCP region with the **Browserless API URL** plugin option. For the MCP option, use an `https://` URL without credentials, query strings or fragments. The hosted MCP server rejects self-hosted URLs, so if you use a self-hosted deployment, set it for the REST skills only and keep the MCP option on a hosted region. A self-hosted-only token will not authenticate to hosted Browserless.

## Plugin Structure

```
.claude-plugin/
  plugin.json           # Plugin metadata and options (token, API URL)
  marketplace.json      # Marketplace catalog for /plugin marketplace add
  icon.png              # Listing icon
.mcp.json               # Hosted Browserless MCP server (adds browserless_agent + tools)
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

## Validate

Check the plugin's structure with Claude Code:

```bash
claude plugin validate . --profile directory --strict
```

## Privacy

See the [Browserless Privacy Policy](https://www.browserless.io/privacy-policy).

## License

SSPL-1.0
