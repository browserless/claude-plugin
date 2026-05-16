---
name: new-landing-page-design
description: Use when the user provides a marketing copy brief (or content document) plus one or more reference page URLs from the browserless-account codebase and wants a new landing page built end-to-end. Triggers on phrases like "new landing page", "build this LP", "here's the copy brief and a reference", or when a long-form brief is pasted with section headings like "SEO title", "Meta description", "[CTAs]", and a list of sections. Runs the full pipeline — discover → decide → plan → implement → verify → PR → monitor — with one round of clarifying questions max.
---

# New Landing Page Design (browserless-account)

End-to-end skill for shipping a new marketing landing page from a copy brief in this repo. Designed to minimise back-and-forth: read the codebase first, decide alone where possible, ask at most one batched round of clarifying questions, then drive all the way through to an open PR + a live feedback monitor.

## Inputs

The user provides:
- **Copy brief** — long-form markdown with section headings (hero, features, CTAs, etc.)
- **1–2 reference page URLs** in this codebase (e.g. `/lp/ai-agents`, `/feature/scraper-api`)
- *Optional* — a screenshot or design mockup

If any are missing, ask once for what's missing before starting.

---

## Phase 1 — Discovery (read-only, ~5–10 min, NO questions to user)

Build a complete mental map BEFORE asking anything. The whole point of this phase is to make later decisions silently instead of pestering the user. Look at:

### 1.1 Reference pages
Read each reference page in full (`src/pages/lp/<slug>.tsx` / `src/pages/feature/<slug>.tsx`). For each, extract:
- Section padding (`py-* lg:py-*`)
- Background alternation pattern (`bg-muted/N`)
- Container shape (`container mx-auto px-4 lg:px-20`, maybe `overflow-hidden`)
- Spacing between `SectionHeading` and content grid (`mt-N`)
- Card padding / gradient / border treatment
- Whether sections use shared components or inline JSX

### 1.2 Shared component inventory
Read `src/components/Marketing/shared.tsx`. Note exports — `HeroSection`, `SectionHeading`, `FeatureCard`, `FeatureGrid`, `FeatureLinkCard`, `CTASection`, `TestimonialCard`, `ComplianceBadges`, `AnimatedSection`, `TrustLogos`, plus animation variants `fadeInUp` and `staggerContainer`. Also read `MarketingLayout.tsx`, `MarketingFooter.tsx`, `CodeBlock.tsx`.

### 1.3 next.config.js exportPathMap
Find the `/lp/*` and `/feature/*` registration block. New routes go here manually — there's no auto-scan.

### 1.4 Constants and data
Grep for anything the brief references (plan names, prices, compliance items, etc.). The most common one: **plan pricing lives in `src/lib/utils.ts` as `PLAN_CONFIG`** — export it if not already exported, then derive `{ name, price, units, overage }` from it. Never hardcode plan tiers.

### 1.5 Available image assets
`ls public/marketing/features/` and sub-dirs. Match the brief's needs against what's there. If nothing pairs visually (e.g. "REST APIs" + "BrowserQL" — `api-collection.svg` and `bql/scraping-ide.svg` don't pair), **switch to icon-based cards** instead of forcing `FeatureLinkCard` with mismatched illustrations.

### 1.6 Footer / nav placement
If brief mentions a footer or nav link, locate `MarketingFooter.tsx` (Use Cases / Resources / Company columns) — link goes there.

### 1.7 Amplitude analytics
Existing pages follow this pattern at the top of the page component:
```tsx
const { track } = useAmplitude(LP_FOO_PAGE_VIEWED_EVENT);
useEffect(() => { track(); }, [track]);
```
The event constant goes in `src/lib/secrets.ts` near the other `*_PAGE_VIEWED_EVENT` constants.

---

## Phase 2 — Decide alone (locked-in defaults)

These are **NOT questions to ask the user**. They are the answers from this codebase. Only deviate if the brief explicitly says otherwise.

| Decision | Default | Why |
|---|---|---|
| Section padding | `py-12 lg:py-16` | scraper-api rhythm — works for 8+ section pages. Use `py-16 lg:py-24` only for short pages (≤5 sections). |
| Alt section bg | `bg-muted/30` | scraper-api default; stronger separation than ai-agents' `bg-muted/20` |
| Container | `container mx-auto px-4 lg:px-20` | Both references |
| Spacing after `SectionHeading` | `mt-16` on the content grid | Both references |
| Hero stats row gap | `gap-8` | ai-agents pattern |
| Card gradient | `bg-gradient-to-br from-card to-card/80` | Both references |
| Card border | `border-border/50` (or `border-primary/30` for emphasis) | Both references |
| Hover treatment on Cards | `transition-all hover:border-primary/30 hover:shadow-xl hover:shadow-primary/5` | shared `FeatureCard` |
| Heading sizes | inherit from shared `HeroSection` / `SectionHeading` / `CTASection` | one source of truth |
| `<h3>` inside cards | `text-lg font-bold text-foreground` (`text-2xl` for emphasis cards) | both references |
| Description text in cards | `text-sm leading-relaxed text-muted-foreground` | both references |
| Animation | `AnimatedSection` wrapper + `m.div` with `staggerContainer`/`fadeInUp` for grids | both references |
| Compliance badges | `<ComplianceBadges />` from shared.tsx (don't roll your own SOC2/HIPAA pills) | already used on home, pricing, scraping, testing, etc. |
| Tabs for code-switchers (e.g. Puppeteer/Playwright) | `Tabs` from `@/components/ui/tabs` | scraper-api Quickstart pattern |
| Final CTA | shared `CTASection` (py-28 lg:py-36 internal) | both references |
| Hero title | `title="..."` + `titleAccent="..."` flowing inline — do NOT wrap title in `<> ... <br /></>` (causes ugly responsive wrapping) | learned the hard way |
| React imports | `import React, { useEffect } from "react"` — required even with new JSX transform because the codebase ESLint config enforces `react/react-in-jsx-scope` | repo convention |

### Diff code blocks (when migration "before / after" is in the brief)
Use `CodeBlock` with `language="diff-javascript"`. The wrapper for each diff line in `renderDiff` must:
- Apply background tint (`bg-red-500/10` / `bg-emerald-500/10`)
- Apply left border (`border-l-2 border-red-500/60` / `border-l-2 border-emerald-500/60`)
- Render the `- ` / `+ ` prefix in its own coloured `<span>` (text-red-400 / text-emerald-400)
- **NOT** set any `text-*` class on the line wrapper itself — that cascades down into Prism's inner spans and flattens every token to one colour. Prism's token classes must win.
- Always wrap every line (including unchanged ones) in `<span class="block">` and `.join("")`. Joining with `"\n"` inside `<pre>` doubles the line breaks.
- Empty lines render as `<span class="block"> </span>` to preserve height.

### Interactive widgets (calculators, sliders, charts)
- Use the existing `recharts` dep (v3.x already in `package.json`), not Chart.js or D3.
- Build as a new `src/components/Marketing/<Name>.tsx` client component (`"use client"`).
- **Lazy-load** via `dynamic(() => import("..."), { ssr: false })` on the consuming page — recharts adds ~80 kB and causes an SSR `ResponsiveContainer` width=-1 warning if rendered on the server.
- Use `Slider` from `@/components/ui/slider` and `Select` from `@/components/ui/select`.
- Use design tokens (`bg-card`, `text-foreground`, `border-border`) so light + dark themes both work. No custom CSS variables.

### Hydration safety for CodeBlock
The bundled Prism at `src/bql/app/utils/prism.js` auto-runs `highlightAll()` on `DOMContentLoaded`, which reorders `<pre>` classes and injects `tabindex="0"` after React hydrates → hydration warning. Set `(Prism as any).manual = true` at module init in `CodeBlock.tsx`. Also `escapeHtml` the fallback path before injecting via `dangerouslySetInnerHTML`.

### When the brief wants pricing-tier comparison logic
Iterate `PLANS` and pick `min(price + max(0, totalUnits - plan.units) * plan.overage)`. **Don't** use `find(p => totalUnits <= p.units * 2)` — that picks the first threshold match and misses the case where a lower tier + overage is cheaper than the next tier's base price.

### When a reference card needs an image but no asset pairs visually
Don't force `FeatureLinkCard` with mismatched hero SVGs. Use an **icon-based card** instead: small `bg-primary/10 rounded-xl` icon square (Code2 / Workflow / Database / Stethoscope / Shield depending on context) + bold title with hover arrow + description + "Learn more →" link. Pattern source: `src/pages/lp/bypass-cloudflare-puppeteer.tsx`.

---

## Phase 3 — Ask at most ONE batched round

After Phase 1+2, use `AskUserQuestion` exactly once with **1–4 questions** for things you genuinely can't infer. Common candidates:

- **URL slug ambiguity** — `/lp/<slug>` (campaign landing page) vs `/feature/<slug>` (long-lived industry/feature page)?
- **Visual fidelity tradeoff** — closer to ref A's pattern or ref B's? Only ask if the two refs genuinely differ on a load-bearing detail (e.g. spacing rhythm)
- **Interactive widget approach** — if the brief includes raw HTML/JS for a calculator-like widget, ask: port to React using existing deps, iframe the raw HTML, or inline via `dangerouslySetInnerHTML`?
- **Diff snippet rendering** — extend `CodeBlock` with diff support vs. show before/after as two cards?

Things to **not** ask:
- Section padding, card styles, animations — all settled in Phase 2 defaults
- Whether to use `FeatureCard` vs custom — use shared
- Whether to add the footer link — if brief says to, do it; if not, don't
- Lint/build standards — repo has them; follow

---

## Phase 4 — Plan (only if in plan mode)

If invoked in plan mode, write the plan to the plan file specified in the system prompt. The plan structure that worked:

```markdown
# <Page name>

## Context
<why this page is being built — buyer journey, competitive context>

## Decisions locked in
<table of decisions made in Phase 2-3>

## Shared infrastructure changes
<extensions to CodeBlock, new shared components, exportPathMap, footer link, secrets.ts events>

## Page <N>: /<route>
<File path, SEO, section-by-section table with component + notes per section>

## Critical files to modify / create
<bullet lists>

## Verification
<commands + manual UX checks>

## Out of scope (defer)
<things explicitly NOT in this PR>
```

Then `ExitPlanMode`. If not in plan mode, skip and proceed straight to Phase 5.

---

## Phase 5 — Implement (order matters)

Do shared infrastructure first so the pages can consume it.

1. **`src/lib/secrets.ts`** — add `LP_FOO_PAGE_VIEWED_EVENT` near the other landing-page constants
2. **`src/components/Marketing/CodeBlock.tsx`** — extend with `diff-*` languages if needed (don't rebuild — extend the existing file)
3. **`src/components/Marketing/<Name>.tsx`** — new interactive component (calculator, etc.) if the brief needs one. Use `recharts`, `Slider`, `Select`, design tokens.
4. **`next.config.js`** — add new route(s) to `exportPathMap`
5. **`src/components/Marketing/MarketingFooter.tsx`** — add footer link if requested
6. **`src/pages/<lp-or-feature>/<slug>.tsx`** — the actual page. Compose from shared components first, custom JSX only when nothing fits.

After each major step, save and continue. Run lint+build at the end of the implementation pass:

```bash
npm run prettier    # auto-fix lint + format
npm run build       # static export verification
```

Fix any errors before moving on. Common ones:
- `'React' must be in scope when using JSX` — add `import React` to the file
- `'X' is defined but never used` — remove unused imports
- Prettier formatting — re-run `npm run prettier`

If a lint pass auto-formats imports and the dynamic-import const ends up between import statements, move it to AFTER all imports.

---

## Phase 6 — Visual verification (always)

Before committing:

1. `npm run dev` (background)
2. Wait for `http://browserless.localhost:3030/<route>` to return 200
3. Use chrome-devtools MCP:
   - `new_page` → the route at 1280×900
   - **Force all Framer Motion sections visible** via `evaluate_script`:
     ```js
     document.querySelectorAll('*').forEach(el => {
       if (el.style && (el.style.opacity === '0' || el.style.transform)) {
         el.style.setProperty('opacity', '1', 'important');
         el.style.setProperty('transform', 'none', 'important');
       }
     });
     ```
     (Full-page screenshots don't trigger `whileInView` because nothing scrolls.)
   - `take_screenshot` full-page, save to `.tmp-screenshots/<slug>.jpeg` (untracked dir)
   - `list_console_messages` filtered to `["error", "warn"]` — fix any hydration warnings before moving on
4. Test interactivity if there's a calculator / tabs / dropdown:
   - `take_snapshot` to get element UIDs
   - `click` tab triggers; verify panels swap
   - Drag a slider via JS keydown `End` / `Home`; verify state updates
5. Resize to 390×844 mobile viewport; screenshot; verify sections stack and tables horizontally scroll
6. Stop dev server with `TaskStop` when done

If any issue surfaces (hydration warning, awkward responsive layout, sliding tabs not working, etc.), fix in place. The goal is to land a polished PR, not a draft that needs a follow-up.

---

## Phase 7 — Open the PR

1. Restore any unrelated working-tree changes that crept in (commonly `public/.well-known/agent-skills/index.json` auto-regenerates — `git restore` it)
2. `git checkout -b feat/<slug>` from `main`
3. Stage **specific files** explicitly. Never `git add .` — too easy to pull in screenshots / unrelated diffs.
4. Commit with a multi-line message via HEREDOC. Co-author trailer per repo convention.
5. `git push -u origin feat/<slug>`
6. `gh pr create --title "feat: <title>" --body "$(cat <<'EOF' ... EOF)"` with sections:
   - **Summary** — bulleted list of pages and what each does
   - **Shared infrastructure** — components added/extended, why
   - **Wiring** — exportPathMap, footer link, secrets.ts
   - **Style decisions** — table mapping each token (`py-12 lg:py-16`, `bg-muted/30`, etc.) to its source reference
   - **Bundle** — First Load JS for new pages vs references
   - **Test plan** — checklist of manual checks
   - **Screenshots** — note that they're in `.tmp-screenshots/` locally; reviewer drag-drops via the web UI (GitHub REST doesn't accept image uploads on comments)
7. If the PR was auto-converted to draft (some repos have an Action for this), call `gh pr ready <num>` after CI passes
8. If `gh pr edit --body-file` later fails with a GraphQL projects deprecation error, use `gh api -X PATCH /repos/{owner}/{repo}/pulls/{num} -f body="..."` instead

---

## Phase 8 — Monitor loop (always set up before finishing)

Set up a persistent `Monitor` watching the PR for:
- Issue-thread comments
- Review submissions
- Inline review comments

```bash
PR=<pr_number>
REPO=<owner>/<repo>
since=$(date -u -v -1M +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '1 minute ago' +%Y-%m-%dT%H:%M:%SZ)
while true; do
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  gh api "repos/$REPO/issues/$PR/comments?since=$since" --jq '.[] | "comment by \(.user.login): \(.body | gsub("\n"; " ") | .[:240])"' 2>/dev/null || true
  gh api "repos/$REPO/pulls/$PR/reviews" --jq ".[] | select(.submitted_at > \"$since\") | \"review by \(.user.login) [\(.state)]: \(.body // \"\" | gsub(\"\n\"; \" \") | .[:200])\"" 2>/dev/null || true
  gh api "repos/$REPO/pulls/$PR/comments" --jq ".[] | select(.created_at > \"$since\") | \"inline \(.path):\(.line // .original_line // 0) by \(.user.login): \(.body | gsub(\"\n\"; \" \") | .[:200])\"" 2>/dev/null || true
  since=$now
  sleep 90
done
```

`persistent: true`, `timeout_ms: 3600000`.

### When feedback arrives

Apply the receiving-code-review pattern:
1. **Verify each finding against the current code** — sometimes the reviewer is wrong, or the issue is already fixed
2. **Fix the real ones** — don't just pattern-match the suggestion
3. **Push back on the rest** with specific reasoning
4. **Reply in-thread**, not as a top-level PR comment:
   ```bash
   gh api -X POST "/repos/$REPO/pulls/$PR/comments/{comment_id}/replies" -f body="..."
   ```
5. Common review patterns and the right response:
   - **"This component is client-only, dynamic-import it"** — yes for heavy widgets (recharts, monaco), no for thin "use client" components (CodeBlock). Match other usages in the codebase.
   - **"This is XSS-vulnerable"** — verify with a grep of all callers. If all are developer-controlled strings today, it's a defensive hardening, not a critical fix. Still apply the escape — it's cheap insurance.
   - **"This algorithm picks the wrong answer at X"** — trace by hand with a concrete value before fixing. If they're right, fix and verify with another value.

If the user weighs in on a design choice that's already implemented, re-verify it's still the best call — sometimes they're pointing at a real readability issue (the diff/Prism interaction in this session) that needs a tweak rather than a revert.

---

## Common pitfalls

| Pitfall | Fix |
|---|---|
| Hardcoded plan prices/units/overage | Export and import `PLAN_CONFIG` from `src/lib/utils.ts` |
| Prism reorders `<pre>` classes on DOMContentLoaded → hydration mismatch | `(Prism as any).manual = true` at module init |
| Diff colour overrides Prism tokens | Move `text-*` off the line wrapper; only the prefix span gets a colour |
| Double-spaced diff rows | `.join("")` not `.join("\n")`; wrap every line in `<span class="block">` |
| Recharts SSR width=-1 warning | `dynamic(..., { ssr: false })` the consuming page |
| Plan picker picks wrong tier | iterate all and `min(price + overage)`, not first threshold match |
| Hero title wrapping ugly on mobile | Drop the `<br />` in the title prop; let `title` + `titleAccent` flow inline |
| `FeatureLinkCard` with mismatched hero SVGs | Switch to icon-based card with "Learn more →" link |
| Full-page screenshot looks empty | Force Framer Motion's `opacity:0`/`transform` to visible via JS before screenshot |
| `gh pr edit --body-file` fails with GraphQL deprecation | Use `gh api -X PATCH /repos/.../pulls/{n} -f body=...` |
| Pre-commit lint error on `'React' must be in scope when using JSX` | Add `import React` even though new JSX transform doesn't need it — repo enforces |
| Auto-classifier blocks screenshots committed to `.github/` | Save to `.tmp-screenshots/` (untracked); tell the user to drag-drop into a PR comment via web UI |

---

## End of run

When the PR is open and the monitor is armed, summarise to the user:
- PR URL
- Deploy preview URL (from the netlify[bot] comment that fires within ~30s of push)
- Bundle size for the new page vs references
- Local screenshot paths for manual drag-drop
- Monitor task ID so they can `TaskStop` it later

Do not mark the todo "complete" for the monitor — leave it `in_progress` so the persistent watch state is visible.
