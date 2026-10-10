---
id: building-blocks/app-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "App Shell"
description: "The HTML template, global CSS, root layout and per-route layout flags that wrap every page."
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
related:
  - building-blocks/frontend-routes
  - building-blocks/frontend-state
  - interfaces/tauri-commands-system
---
# App Shell

The app shell is the set of files that frame each page before route code runs.

## Files
- src/app.html: HTML template with `%sveltekit.head%` and `%sveltekit.body%` and a dark body background.
- src/app.css: global reset, font stack and dark colours.
- src/app.d.ts: empty `App` namespace declarations.
- src/routes/+layout.svelte: on mount calls `appState.loadConfig()`; under Tauri it invokes `check_prerequisites` and sets `appState.ffmpegAvailable`; it shows an error banner when ffmpeg is missing.
- src/routes/+layout.ts and src/routes/widget/+layout.ts: each export `ssr = false` and `prerender = true`.

## Uses
- `appState` and `isTauri` from [Frontend State](./frontend-state.md).
- The `check_prerequisites` command, see [Tauri Command: check_prerequisites in the layout](../interfaces/tauri-commands-system.md).

## Related
- [Frontend Routes](./frontend-routes.md)
