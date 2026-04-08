---
name: download
description: Run custom Puppeteer code and capture files downloaded by Chrome during execution. Use when the user needs to download files from websites, export CSVs, grab PDFs, or programmatically trigger and retrieve any file download from a webpage.
---

# Download

Use the Browserless `/download` REST API to execute custom Puppeteer code and capture any files that Chrome downloads during execution.

The user's request is: "$ARGUMENTS"

## How to call

Make a POST request to the Browserless download endpoint:

```
POST ${BROWSERLESS_API_URL}/download?token=${BROWSERLESS_TOKEN}
Content-Type: application/javascript
```

OR with JSON payload:

```
POST ${BROWSERLESS_API_URL}/download?token=${BROWSERLESS_TOKEN}
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

### Option 1: JavaScript body (Content-Type: application/javascript)

Send raw JavaScript code directly. The function receives a `page` (Puppeteer Page) and optional `context` object. The code should trigger a file download — the API captures and returns the downloaded file.

```javascript
export default async ({ page }) => {
  await page.goto("https://example.com/reports");
  const downloadButton = await page.waitForSelector("#download-csv");
  await downloadButton.click();
};
```

### Option 2: JSON body (Content-Type: application/json)

```json
{
  "code": "export default async ({ page, context }) => { await page.goto(context.url); const btn = await page.waitForSelector('#download'); await btn.click(); };",
  "context": {
    "url": "https://example.com/reports"
  }
}
```

Parameters:
- `code` (string, required): ESM JavaScript code. Must export a default async function that receives `{ page, context }` and triggers a file download.
- `context` (object, optional): Data passed into the function for dynamic behavior.

### Response

The response contains the downloaded file as binary data with appropriate `Content-Type` and `Content-Disposition` headers matching the downloaded file.

## Execution

Use `curl` via Bash to make the request. Save the output to a file using `-o` since the response is binary. Example:

```bash
source ~/.browserless/.env 2>/dev/null
curl -s -X POST "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}/download?token=$BROWSERLESS_TOKEN" \
  -H "Content-Type: application/javascript" \
  -o downloaded_file \
  -d 'export default async ({ page }) => {
  await page.goto("https://example.com/reports");
  const btn = await page.waitForSelector("#download-csv");
  await btn.click();
};'
```

Write the Puppeteer code based on the user's requirements. The code should navigate to the target page and trigger the download action (clicking a button, submitting a form, etc.). Always save the response to a file with `-o` since it's binary content. Use `-D -` or `-i` to inspect response headers if you need to determine the file type.
