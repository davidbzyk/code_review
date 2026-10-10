---
id: building-blocks/frontend-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend shell
description: Page template, global styles, layout and route options shared by all pages.
domain: architecture
tags:
  - building-block
  - frontend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/app.html
  - resource: src/app.css
  - resource: src/app.d.ts
  - resource: src/routes/+layout.svelte
  - resource: src/routes/+layout.ts
  - resource: src/routes/widget/+layout.ts
  - resource: src/lib/index.ts
related:
  - building-blocks/frontend-state-and-logging
  - building-blocks/backend-prerequisites
  - crosscutting/state-management
---

The shell wraps every route with global CSS, loads configuration once and shows an ffmpeg warning banner.

## Files
- src/app.html: HTML template with `%sveltekit.head%` and `%sveltekit.body%`; body has `data-sveltekit-preload-data="hover"`.
- src/app.css: resets margins, dark background `#0f172a`, text colour `#f1f5f9`, `box-sizing: border-box`.
- src/app.d.ts: empty `App` namespace declarations.
- src/routes/+layout.svelte: imports `../app.css`; in `onMount` awaits `appState.loadConfig()`, and under `isTauri()` invokes `check_prerequisites` and sets `appState.ffmpegAvailable`. Renders an error banner with install hints when it is false, then `{@render children()}`.
- src/routes/+layout.ts and src/routes/widget/+layout.ts: `ssr = false`, `prerender = true`.
- src/lib/index.ts: a placeholder comment for `$lib` imports.

## Uses
`appState` and `isTauri` from src/lib/state.svelte.ts; the Rust command `check_prerequisites` ([[building-blocks/backend-prerequisites]]).

## Related
[[building-blocks/frontend-state-and-logging]], [[building-blocks/backend-prerequisites]], [[crosscutting/state-management]]
