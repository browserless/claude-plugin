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

This will prompt you for your token and preferred API region (SFO, LON, or a custom URL), then save the credentials to `~/.browserless/.env`.

Alternatively, set the environment variable directly:

```bash
export BROWSERLESS_TOKEN=your-token-here
```

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

It reuses the same credentials: set `BROWSERLESS_TOKEN` (env var or via `/browserless:auth`). With no token, the hosted endpoint falls back to OAuth sign-in.

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

Credentials are stored in `~/.browserless/.env` with `600` permissions. The token resolution order is:

1. `BROWSERLESS_TOKEN` environment variable (if set in shell)
2. `~/.browserless/.env` file (written by `/browserless:auth`)

## API Regions

| Region | URL |
|--------|-----|
| SFO (US West, default) | `https://production-sfo.browserless.io` |
| LON (Europe) | `https://production-lon.browserless.io` |
| Custom | Any self-hosted or custom Browserless URL |

## Plugin Structure

```
.claude-plugin/
  plugin.json           # Plugin metadata
.mcp.json               # Hosted Browserless MCP server (adds browserless_agent + tools)
hooks/
  hooks.json            # SessionStart hook config
scripts/
  check-auth.sh         # Warns if token is not configured
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

## License

SSPL-1.0
