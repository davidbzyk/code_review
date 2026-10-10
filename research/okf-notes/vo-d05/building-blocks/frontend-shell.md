---
id: building-blocks/frontend-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend shell and utilities
description: Shared frontend files: HTML shell, global CSS, layout, Tauri invoke wrapper, blob store and logger.
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
  - resource: src/lib/tauri.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/logger.ts
related:
  - building-blocks/frontend-state
  - building-blocks/frontend-routes
  - crosscutting/logging
---

# Frontend shell and utilities

These files wrap every page: the HTML template, the root layout, and three small helper modules.

## Files and exposure

- `src/app.html` is the page template with `%sveltekit.head%` and `%sveltekit.body%`; `src/app.css` sets the dark background and font.
- `src/routes/+layout.svelte` runs `appState.loadConfig()` on mount and, in Tauri, calls `check_prerequisites` to set `appState.ffmpegAvailable`; it shows an "ffmpeg not found" banner when false.
- `src/routes/+layout.ts` and `src/routes/widget/+layout.ts` export `ssr = false` and `prerender = true`.
- `src/lib/tauri.ts` exports `tauriInvoke<T>(cmd, args)`, which lazily imports `@tauri-apps/api/core` and calls `invoke`.
- `src/lib/blobStore.ts` exports `blobStore` with `setVideo`, `getVideo`, `setAudio`, `getAudio`, `clear`; it holds browser-mode recordings in module variables.
- `src/lib/logger.ts` exports `logger`, which writes prefixed `[VO:category]` lines to the console.
- `src/lib/index.ts` is a comment-only placeholder for the `$lib` alias; `src/app.d.ts` declares an empty `App` namespace.

## Uses

- Layout uses `appState` ([[building-blocks/frontend-state]]).
- Pages and libraries import `tauriInvoke`, `blobStore` and `logger` ([[building-blocks/frontend-routes]]).

## Related

- [[building-blocks/frontend-state]] - Frontend state and Drive client
- [[building-blocks/frontend-routes]] - Frontend routes
- [[crosscutting/logging]] - Logging
