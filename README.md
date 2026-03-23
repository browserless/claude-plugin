# Browserless Plugin for Claude Code

A Claude Code plugin that gives Claude direct access to the [Browserless.io](https://docs.browserless.io/rest-apis/intro) REST APIs: scrape webpages, take screenshots, generate PDFs, search the web, map site structures, and run custom browser automation, all from natural language.

## Installation

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
/browserless:screenshot https://example.com
/browserless:pdf https://example.com
/browserless:search what is browserless
/browserless:map https://example.com
/browserless:function click the login button on https://example.com
```

## Skills

| Skill | Command | Description | Example Prompt |
|-------|---------|-------------|----------------|
| **Auth** | `/browserless:auth` | Configure API token and region. Subcommands: `status`, `clear`, `region`. | |
| **Smart Scrape** | `/browserless:smart-scrape` | Scrape webpages with cascading strategies (HTTP fetch, proxy, headless browser, captcha solving). Returns markdown, HTML, screenshots, PDFs, or links. | `summarize the main content of https://news.ycombinator.com` |
| **Screenshot** | `/browserless:screenshot` | Capture screenshots of webpages. Supports full-page, element-specific, viewport sizing, image formats (PNG/JPEG/WebP), and proxy/geo-targeting. | `take a screenshot of https://inet-ip.info/ using a French proxy, wait 5 seconds before taking it` |
| **PDF** | `/browserless:pdf` | Generate PDFs from webpages or HTML. Supports paper formats, margins, headers/footers, landscape, background graphics, and tagged/accessible PDFs. | `save https://en.wikipedia.org/wiki/Headless_browser as a landscape A4 PDF` |
| **Search** | `/browserless:search` | Search the web and optionally scrape result pages. Supports web, news, and image sources with time-based filtering and content categories. | `find recent AI news en español from the last week` |
| **Map** | `/browserless:map` | Discover and list all URLs on a website. Crawls sitemaps, pages, and subdomains with relevance-based search filtering. | `save a list of all URLs on https://browserless.io in json format` |
| **Function** | `/browserless:function` | Execute custom Puppeteer JavaScript in a cloud browser. Run arbitrary automation scripts, interact with page elements, fill forms, and return structured data. | `go to https://news.ycombinator.com and return the top 10 story titles as JSON` |


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
plugins/browserless/
  .claude-plugin/
    plugin.json           # Plugin metadata
  hooks/
    hooks.json            # SessionStart hook config
  scripts/
    check-auth.sh         # Warns if token is not configured
  skills/
    auth/SKILL.md         # Authentication setup
    smart-scrape/SKILL.md # Web scraping
    screenshot/SKILL.md   # Screenshot capture
    pdf/SKILL.md          # PDF generation
    search/SKILL.md       # Web search
    map/SKILL.md          # URL discovery
    function/SKILL.md     # Custom Puppeteer code
```

## API Reference

Each skill maps to a Browserless REST API endpoint. Full API documentation is available at [docs.browserless.io/rest-apis/intro](https://docs.browserless.io/rest-apis/intro).

| Skill | Endpoint |
|-------|----------|
| Smart Scrape | `POST /smart-scrape` |
| Screenshot | `POST /screenshot` |
| PDF | `POST /pdf` |
| Search | `POST /search` |
| Map | `POST /map` |
| Function | `POST /function` |

## License

SSPL-1.0
