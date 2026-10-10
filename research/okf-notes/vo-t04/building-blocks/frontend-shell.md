---
id: building-blocks/frontend-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend shell"
description: "The shell holds the HTML template, global CSS, the root layout that loads config and checks ffmpeg, and the per-route rendering flags."
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
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/frontend-pages
    - runtime/app-startup
---
# Frontend shell

The frontend shell is the set of files every route shares.

## Files

- src/app.html: HTML template with `%sveltekit.head%` and `%sveltekit.body%`; the body sets `data-sveltekit-preload-data="hover"`.
- src/app.css: resets margin and padding, sets the font stack, a dark background (`#0f172a`) and `box-sizing: border-box`.
- src/app.d.ts: an empty `App` namespace declaration.
- src/lib/index.ts: a comment only, for `$lib` imports.
- src/routes/+layout.ts and src/routes/widget/+layout.ts: each exports `ssr = false` and `prerender = true`.
- src/routes/+layout.svelte: on mount it calls `appState.loadConfig()`; in Tauri it also invokes `check_prerequisites` and stores `ffmpeg_available` in `appState.ffmpegAvailable`. It renders a red banner with install hints when ffmpeg is not available, then the child route.

## Uses

`appState` and `isTauri` from src/lib/state.svelte.ts; `invoke` from `@tauri-apps/api/core`.

## Related

[[building-blocks/frontend-state]], [[building-blocks/frontend-pages]], [[runtime/app-startup]]
