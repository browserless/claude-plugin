# Browserless Plugin for Claude Code

A Claude Code plugin that connects Claude to the authenticated [Browserless MCP server](https://mcp.browserless.io/mcp): scrape webpages, take screenshots, generate PDFs, search the web, map site structures, and run custom browser automation, all from natural language. Every skill uses MCP; none reads local API credentials or authenticates REST requests from the shell.

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

- **Browserless API token** (required): used by the hosted MCP server for all skills. Enter it in the plugin configuration UI, not in conversation. The plugin declares this option with `sensitive: true`; Claude Code manages its storage and sends it through the configured MCP Authorization header.
- **Browserless API URL**: the hosted region the MCP server uses. Defaults to `https://production-sfo.browserless.io`. See [API Regions](#api-regions).

To change them later, run `/plugin configure browserless@browserless`, then restart Claude Code or reconnect Browserless in `/mcp` to apply them.

### 3. Check the connection

Open `/mcp` and check that the plugin's `plugin:browserless:browserless` server is connected, not just another Browserless server. For configuration guidance, run:

```
/browserless:auth
```

This skill directs you to Claude Code's plugin configuration; it does not ask for a token in chat, read or write credential files, or print token prefixes. A connected status does not prove that an API token will be accepted by every operation; authentication failures are reported by the tools.

### Migrating from local REST credentials

All skills now use the same MCP plugin options. Configure your hosted token and region once through `/plugin configure browserless@browserless`, then reconnect. Old local credential files and environment overrides are no longer used or automatically imported. The plugin leaves them untouched; it does not inspect or delete them.

**Self-hosted limitation:** this migration removes the plugin's direct REST path. Arbitrary self-hosted Browserless endpoints and self-hosted-only tokens are not supported. Do not enter a self-hosted-only token into the hosted MCP configuration. Use a separate, independently configured integration for self-hosted deployments; this plugin does not provide a shell fallback.

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
| **Auth** | `/browserless:auth` | Guidance for plugin configuration, connection status, region changes, and disabling the connection. | |
| **Agent** | `/browserless:agent` | Interactive, stateful browser session (via the MCP server) — navigate, click, type, log in, handle captchas/cookie banners, multi-step flows, file up/downloads. | `log into https://example.com and download my latest invoice` |
| **Smart Scrape** | `/browserless:smart-scrape` | Scrape webpages with cascading strategies (HTTP fetch, proxy, headless browser, captcha solving). Returns markdown, HTML, screenshots, PDFs, or links. | `summarize the main content of https://news.ycombinator.com` |
| **Search** | `/browserless:search` | Search the web and optionally scrape result pages. Supports web, news, and image sources with time-based filtering and content categories. | `find recent AI news en español from the last week` |
| **Map** | `/browserless:map` | Discover and list all URLs on a website. Crawls sitemaps, pages, and subdomains with relevance-based search filtering. | `save a list of all URLs on https://browserless.io in json format` |
| **Function** | `/browserless:function` | Execute custom Puppeteer JavaScript in a cloud browser. Run arbitrary automation scripts, interact with page elements, fill forms, and return structured data. | `go to https://example.com and return the page title and all link texts as JSON` |
| **Export** | `/browserless:export` | Export a webpage in its native format, optionally bundling all resources (CSS, JS, images) into a ZIP archive for offline use. | `save https://example.com with all assets as a ZIP` |
| **Performance** | `/browserless:performance` | Run a Lighthouse audit on a webpage. Get scores for performance, accessibility, best practices, SEO, and PWA. | `audit the performance and accessibility of https://example.com` |
| **Crawl** | `/browserless:crawl` | Crawl an entire website starting from a seed URL, following links to configurable depth while scraping all discovered pages. | `crawl https://docs.browserless.io up to 3 levels deep` |

> Screenshots, PDFs, and file downloads no longer have standalone skills — they're covered by `/browserless:smart-scrape` (screenshot/pdf via output formats) and `/browserless:agent` (downloads during a flow).


## MCP Server (all skills)

Installing this plugin registers the hosted **Browserless MCP server** (`https://mcp.browserless.io/mcp?mcpSource=claude-plugin`) as `plugin:browserless:browserless`. Every operation uses only this server's tools (`mcp__plugin_browserless_browserless__*`), including scraping, search, map, function, export, performance and crawl. `browserless_agent` provides an interactive browser session for multi-step work. If the plugin's tool is missing, skills stop with configuration guidance rather than silently using another connection's account or region. Self-hosted requests require your agreement before any work runs on hosted Browserless; the plugin does not offer REST alternatives.

The fixed `mcpSource=claude-plugin` query parameter is a non-secret attribution tag. It distinguishes the plugin URL from a manually added `https://mcp.browserless.io/mcp` connection, preventing Claude Code's duplicate-URL suppression; it does not change authentication, region, or artifact delivery.

The MCP server authenticates with the plugin's options. Claude Code sends the **Browserless API token** as the `Authorization` header and the **Browserless API URL** as `x-browserless-api-url`. The plugin runs no local scripts or helpers. Because an `Authorization` header is always configured, Claude Code doesn't offer OAuth sign-in for this server: set the token instead.

### Authenticated artifact saving

The plugin requests native artifact delivery with the fixed, non-secret header `x-browserless-artifact-delivery: mcp-resource`. Reconnect after changing this preference; it is fixed for each MCP session. This header grants no access and does not certify a client's saving behavior.

**Release prerequisite:** deploy a server that supports this contract and pass an authenticated production smoke test before releasing this plugin change. An older server may ignore the header and return legacy instructions; the agent skill treats that as unsupported saving, not permission to fetch local credentials.

Saving requires Claude Code CLI **2.1.327 or newer on Linux or macOS**, an explicit `ReadMcpResourceTool` that saves binary resources to disk and returns only `blobSavedTo` metadata, and decoded files **up to 10 MiB**. Version alone is not a safety guarantee: unknown or inline resource handling is unsupported. Linux 2.1.327 was exercised with PDF, ZIP, PNG, saved JSON and size boundaries using a deterministic model; macOS 2.1.327 has a reported real-model exact-byte 1 MiB save. Neither establishes safety on every later release. Claude Desktop and other MCP clients remain unverified.

Checking the client version may also require shell permission for `claude --version`. If that approval is unavailable, a headless run may stop before fetching the resource. Interactive users may see this additional approval prompt before the copy prompt. A `blobSavedTo` result confirms disk saving only after a read; it is not a substitute for establishing safe client handling before the first read.

The agent checks file existence and byte count through metadata, then copies the file to your destination. **Copying from Claude Code's sensitive `~/.claude` directory requires permission approval.** If approval is denied or unavailable, including headless runs, saving stops and reports the limitation. The skill forbids `Read`, `cat`, image viewers, or other content inspection of `blobSavedTo` or the destination copy as a save fallback. With the revised skill text explicitly loaded, Linux CLI 2.1.327 and Sonnet 4.6 stopped safely in three denied-copy runs and saved exact bytes in three explicitly approved controls, with no image payload in 21 captured model requests. The old text also stopped safely on Linux, so Linux did not reproduce the originally reported macOS leak. Subsequent operator-reported real-model macOS verification confirmed three headless denied-copy runs with `Read` available: each stopped after the protected-path refusal, with no `Read` call, base64 or token in the transcripts. Two approved-copy controls saved a byte-exact 1 MiB file and a valid PNG, with zero `Read` calls. Intentional inline image analysis is separate and still enters model context.

Artifacts remain authenticated and owner-scoped. The URI is an identifier, not a bearer link. MCP and existing authenticated HTTP downloads share single-use consumption, a 15-minute expiry, and earlier session cleanup. Claude Code rejects SSE events above 16 MB, so the native route has a conservative 10 MiB limit; the existing HTTP route retains its 50 MiB limit. Larger files or unavailable saving tools are reported as unsupported without reading the resource, fetching credentials, or regenerating browser work automatically.

The function, export, smart-scrape and performance skills share the agent skill's safe-saving instructions. Export and function use `toDisk: true` for files to keep; smart-scrape uses it for screenshot/PDF attachments. Intentional text extraction still enters model context. Directory policy review remains separate from local validation.

**Troubleshooting:**

- **Browserless is missing from `/mcp`:** Claude Code doesn't start the server until the required API token is set. Run `/plugin configure browserless@browserless`, enter the token, then restart Claude Code.
- **A manual Browserless connection is already installed:** Claude Code can hide a plugin server when another MCP entry has the identical URL. The plugin's tagged URL avoids a clash with the usual untagged manual entry. To use only the plugin's token, region and native artifact saving, remove the old manual entry with `claude mcp remove browserless` (substitute its actual name and scope if different), then reconnect or restart. Remove it only if you no longer need that separate connection. If the plugin server is still missing, check `/mcp` for another entry with the exact tagged URL; another server's tools are not a substitute.
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

### MCP capability limits

The skills follow the connected tool schemas rather than sending REST-only parameters. In particular:

- Crawl starts a job and normally waits server-side for results. The current MCP tool does not expose listing, cancellation, webhooks, or resuming/status-checking an existing crawl. A timeout may leave the crawl running; the skill reports the returned ID and limitation instead of restarting it or polling REST.
- Crawl returns bounded content, not a complete site archive: full content is fetched for at most 50 completed pages and displayed content is capped.
- Map does not expose the REST `location` option. Restricted MCP endpoints may also omit other options or tools; the plugin reports unsupported capabilities instead of bypassing those restrictions.
- Function results are returned directly, not wrapped in `{ data, type }`. Performance may return a pending widget; the skill waits for that result rather than starting duplicate audits or polling.

## Auth Management

| Command | Description |
|---------|-------------|
| `/browserless:auth` | Explain setup through the plugin configuration UI |
| `/browserless:auth status` | Explain how to check the connection in `/mcp`, without inspecting secrets |
| `/browserless:auth clear` | Explain how to disable or uninstall the plugin; does not delete stored credentials |
| `/browserless:auth region` | Explain how to change the hosted region through plugin configuration |
| `/plugin configure browserless@browserless` | Set the token and hosted API URL used by all skills |

Only Claude Code's configured MCP connection handles the API token. The skills do not read it from files or environment variables, copy it into tool arguments, or ask for it in chat. Disabling the plugin stops using its connection; it does not establish that stored credentials were deleted.

## API Regions

| Region | URL | Supported by |
|--------|-----|--------------|
| SFO (US West, default) | `https://production-sfo.browserless.io` | All skills through hosted MCP |
| LON (London) | `https://production-lon.browserless.io` | All skills through hosted MCP |
| AMS (Amsterdam) | `https://production-ams.browserless.io` | All skills through hosted MCP |
| Other hosted | Valid `browserless.io` URLs, including `https://chrome.browserless.io` and dedicated subdomains | All skills through hosted MCP |
| Self-hosted | Arbitrary non-Browserless URLs | Not supported by this plugin |

Set the region with the **Browserless API URL** plugin option. Use an `https://` URL without credentials, query strings or fragments. The hosted MCP server rejects self-hosted URLs; changing this option does not make it a general-purpose proxy to arbitrary endpoints.

## Plugin Structure

```
.claude-plugin/
  plugin.json           # Plugin metadata and options (token, API URL)
  marketplace.json      # Marketplace catalog for /plugin marketplace add
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

## Tool Reference

Each skill calls the corresponding MCP tool using the schema exposed by the connected server. The REST documentation at [docs.browserless.io/rest-apis/intro](https://docs.browserless.io/rest-apis/intro) describes the underlying APIs, not the plugin's authentication or tool argument contracts.

| Skill | MCP tool |
|-------|----------|
| Agent | `browserless_agent` |
| Smart Scrape | `browserless_smartscraper` |
| Search | `browserless_search` |
| Map | `browserless_map` |
| Function | `browserless_function` |
| Export | `browserless_export` |
| Performance | `browserless_performance` |
| Crawl | `browserless_crawl` |

## Validate

Check the plugin's structure with Claude Code:

```bash
claude plugin validate . --profile directory --strict
```

## Privacy

See the [Browserless Privacy Policy](https://www.browserless.io/privacy-policy).

## License

SSPL-1.0
