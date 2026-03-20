---
name: screenshot
description: Capture a screenshot of a webpage using the Browserless screenshot API. Supports full-page captures, viewport-only, and multiple image formats (PNG, JPEG, WebP). Use when the user wants to take a screenshot or capture a visual snapshot of a webpage.
---

# Screenshot

Use the Browserless `/screenshot` REST API to capture a screenshot of a webpage.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless screenshot endpoint:

```
POST ${BROWSERLESS_API_URL}/screenshot?token=${BROWSERLESS_TOKEN}
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
    "fullPage": true,
    "type": "png"
  }
}
```

#### Top-level parameters:

- `url` (string): Website URL to capture. Use this OR `html`, not both.
- `html` (string): Inline HTML content to render instead of a URL.
- `selector` (string): CSS selector to target a specific element instead of the full page.
- `scrollPage` (boolean): Scroll through the entire page before capturing. Useful for triggering lazy-loaded content.
- `blockConsentModals` (boolean): Automatically block cookie consent modals and popups.
- `bestAttempt` (boolean): Proceed when awaited events (goto, waitForSelector, etc.) fail or timeout.
- `emulateMediaType` (string): Change CSS media type of the page (e.g., `"screen"`, `"print"`).
- `setJavaScriptEnabled` (boolean): Whether to allow JavaScript to run on the page.
- `userAgent` (object): Custom user agent. Properties: `userAgent` (string), `platform` (string).

#### `options` (object) — Puppeteer ScreenshotOptions:

- `fullPage` (boolean): Capture the entire scrollable page vs just the viewport.
- `type` (string): Image format — `"png"`, `"jpeg"`, or `"webp"`.
- `quality` (number): Image quality 0–100. Only applies to `"jpeg"` and `"webp"`. Not applicable to `"png"`.
- `omitBackground` (boolean): Hide default white background for transparent screenshots.
- `clip` (object): Region of the page to clip. Required properties: `x` (number), `y` (number), `width` (number), `height` (number). Optional: `scale` (number).
- `encoding` (string): `"base64"` or `"binary"`.
- `captureBeyondViewport` (boolean): Capture beyond the viewport.
- `fromSurface` (boolean): Capture from the surface rather than the view.
- `optimizeForSpeed` (boolean): Optimize encoding for speed over size.

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

#### `waitForTimeout` (number): Wait N milliseconds before capturing.

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

The API returns **binary image data** directly with the appropriate `Content-Type` header (`image/png`, `image/jpeg`, or `image/webp`).

## Execution

Use `curl` via Bash to make the request. Save the output to a file with the appropriate extension. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/screenshot?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "options": {"fullPage": true, "type": "png"}}' \
  -o screenshot.png
```

After saving, inform the user of the file path. If the user hasn't specified an output path, save to the current working directory with a descriptive filename.
