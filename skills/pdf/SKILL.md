---
name: pdf
description: Generate a PDF document from a webpage or HTML content using the Browserless PDF API. Supports page formatting, headers/footers, and background graphics. Use when the user wants to convert a webpage to PDF or generate a PDF from HTML.
---

# PDF

Use the Browserless `/pdf` REST API to generate a PDF from a webpage or HTML content.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless PDF endpoint:

```
POST ${BROWSERLESS_API_URL}/pdf?token=${BROWSERLESS_TOKEN}
Content-Type: application/json
```

## Authentication

Before making the request, source the saved credentials and resolve the token:

```bash
source ~/.browserless/.env 2>/dev/null
```

The token is resolved in this order:
1. `$BROWSERLESS_TOKEN` environment variable (if already set in the shell)
2. `~/.browserless/.env` file (written by `/browserless:auth`)
3. If neither exists, ask the user to run `/browserless:auth` to configure their token

For the API URL, use `$BROWSERLESS_API_URL` if set, otherwise default to `https://production-sfo.browserless.io`.

### Query parameters

These are appended to the URL as query parameters (e.g., `?token=...&blockAds=true`):

- `token` (string): Authorization token (handled by auth, see above).
- `blockAds` (boolean): Load ad-blocking extensions (uBlock-Lite) for the session. May cause some sites to not load properly.
- `timeout` (number): Override system-level timeout in milliseconds.
- `trackingId` (string): Custom session identifier.
- `proxy` (string): Proxy type, currently only `"residential"` is supported.
- `proxyCountry` (string): Two-letter country code (US, GB, FR, DE, etc.).
- `proxyCity` (string): City for proxy routing.
- `proxyState` (string): State/province for proxy (use underscores for whitespace).
- `proxySticky` (string): Use the same IP for all requests. Values: `"true"`, `"false"`, `"1"`, `"0"`.
- `proxyLocaleMatch` (string): Match browser language to proxy location. Values: `"true"`, `"false"`, `"1"`, `"0"`.
- `proxyPreset` (string): Preset code for website-specific proxy routing (e.g., `"px_gov01"`, `"px_amazon01"`).
- `externalProxyServer` (string): User-provided proxy URL. Format: `http(s)://[username:password@]host:port`.
- `launch` (object|string): Browser launch options (headless, args, defaultViewport, etc.).

### Request body

```json
{
  "url": "<target URL>",
  "options": {
    "printBackground": true,
    "format": "A4"
  }
}
```

#### Top-level parameters:

- `url` (string): Webpage URL to convert. Use this OR `html`, not both.
- `html` (string): Inline HTML content to render as PDF.
- `blockConsentModals` (boolean): Automatically block cookie consent modals and popups.
- `bestAttempt` (boolean): Proceed when awaited events (goto, waitForSelector, etc.) fail or timeout.
- `emulateMediaType` (string): Change CSS media type of the page (e.g., `"screen"`, `"print"`).
- `setJavaScriptEnabled` (boolean): Whether to allow JavaScript to run on the page.
- `userAgent` (object): Custom user agent. Properties: `userAgent` (string), `platform` (string).

#### `options` (object) — Puppeteer PDFOptions:

- `format` (string): Paper format — `"Letter"`, `"Legal"`, `"Tabloid"`, `"Ledger"`, `"A0"`, `"A1"`, `"A2"`, `"A3"`, `"A4"`, `"A5"`, `"A6"`.
- `width` (string|number): Paper width. Can be a number (pixels) or string with unit (e.g., `"8.5in"`).
- `height` (string|number): Paper height. Can be a number (pixels) or string with unit (e.g., `"11in"`).
- `scale` (number): Scale of the webpage rendering. Must be between `0.1` and `2`.
- `landscape` (boolean): Print in landscape orientation.
- `printBackground` (boolean): Print background graphics/colors.
- `displayHeaderFooter` (boolean): Show header and footer.
- `headerTemplate` (string): HTML template for the header. Supports classes: `date`, `title`, `url`, `pageNumber`, `totalPages`.
- `footerTemplate` (string): HTML template for the footer. Same classes as `headerTemplate`.
- `pageRanges` (string): Paper ranges to print, e.g., `"1-5, 8, 11-13"`.
- `margin` (object): PDF margins. Properties: `top`, `bottom`, `left`, `right` — each a string (e.g., `"1cm"`) or number.
- `preferCSSPageSize` (boolean): Give CSS `@page` size priority over `width`/`height`/`format`.
- `omitBackground` (boolean): Hide default white background for transparent PDFs.
- `tagged` (boolean): Generate tagged (accessible) PDF.
- `outline` (boolean): Generate document outline.
- `fullPage` (boolean): Capture the full page.
- `timeout` (number): PDF generation timeout in ms. Pass `0` to disable.
- `waitForFonts` (boolean): Wait for `document.fonts.ready` to resolve before generating.

#### `gotoOptions` (object) — Navigation options:

- `waitUntil` (string|array): When navigation is considered done — `"load"`, `"domcontentloaded"`, `"networkidle0"`, `"networkidle2"`. Can be an array of events.
- `timeout` (number): Navigation timeout in ms. Pass `0` to disable.
- `referer` (string): Referer header value.
- `referrerPolicy` (string): Referrer-policy header value.

#### `viewport` (object) — Page viewport:

- `width` (number, required): Page width in CSS pixels.
- `height` (number, required): Page height in CSS pixels.
- `deviceScaleFactor` (number): Device scale factor (DPR).
- `isMobile` (boolean): Whether `meta viewport` tag is considered.
- `isLandscape` (boolean): Landscape mode.
- `hasTouch` (boolean): Enable touch events.

#### `authenticate` (object) — HTTP authentication:

- `username` (string, required): Username.
- `password` (string, required): Password.

#### `cookies` (array) — Cookies to set before navigation:

Each cookie object: `name` (string, required), `value` (string, required), `url` (string), `domain` (string), `path` (string), `secure` (boolean), `httpOnly` (boolean), `sameSite` (`"Strict"`, `"Lax"`, `"None"`), `expires` (number), `priority` (`"Low"`, `"Medium"`, `"High"`).

#### `waitForSelector` (object) — Wait for a CSS selector:

- `selector` (string, required): CSS selector to wait for.
- `timeout` (number): Max wait time in ms.
- `visible` (boolean): Wait for element to be visible.
- `hidden` (boolean): Wait for element to be hidden.

#### `waitForFunction` (object) — Wait for a JS function:

- `fn` (string, required): JavaScript function/statement to evaluate in browser context.
- `timeout` (number): Max wait time in ms. Default 30000.
- `polling` (string|number): Polling interval — `"raf"`, `"mutation"`, or a number in ms.

#### `waitForEvent` (object) — Wait for a page event:

- `event` (string, required): Event name to wait for.
- `timeout` (number): Max wait time in ms.

#### `waitForTimeout` (number): Wait N milliseconds before generating.

#### `addScriptTag` (array) — Scripts to inject:

Each object: `url` (string), `path` (string), `content` (string), `type` (string — use `"module"` for ES2015), `id` (string).

#### `addStyleTag` (array) — CSS to inject:

Each object: `url` (string), `path` (string), `content` (string).

#### `setExtraHTTPHeaders` (object): Key-value pairs of additional HTTP headers for every request.

#### `rejectRequestPattern` (array of strings): URL patterns to reject. Matching requests are aborted.

#### `rejectResourceTypes` (array of strings): Resource types to reject. Values: `"document"`, `"stylesheet"`, `"image"`, `"media"`, `"font"`, `"script"`, `"texttrack"`, `"xhr"`, `"fetch"`, `"prefetch"`, `"eventsource"`, `"websocket"`, `"manifest"`, `"signedexchange"`, `"ping"`, `"cspviolationreport"`, `"preflight"`, `"other"`.

#### `requestInterceptors` (array) — Mock or modify network requests:

Each object: `pattern` (string, required — regex matched against request URL), `response` (object, required — with `status` (number), `contentType` (string), `body` (string), `headers` (object)).

### Response

The API returns **binary PDF data** with `Content-Type: application/pdf` and `Content-Disposition: attachment; filename="output.pdf"`.

## Execution

Use `curl` via Bash to make the request. Save the output to a `.pdf` file. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/pdf?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "options": {"printBackground": true, "format": "A4"}}' \
  -o output.pdf
```

After saving, inform the user of the file path. If the user hasn't specified an output path, save to the current working directory with a descriptive filename.
