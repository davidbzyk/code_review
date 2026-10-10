---
id: building-blocks/frontend-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend shell and static assets"
description: "Root layout, HTML template, global CSS and route options of the SvelteKit app."
domain: architecture
tags:
  - frontend
  - layout
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/routes/+layout.svelte
  - resource: src/routes/+layout.ts
  - resource: src/routes/widget/+layout.ts
  - resource: src/app.html
  - resource: src/app.css
  - resource: src/app.d.ts
  - resource: src/lib/index.ts
  - resource: src/lib/assets/favicon.svg
related:
  - building-blocks/frontend-state
  - building-blocks/backend-ffmpeg
  - interfaces/tauri-commands
---

# Frontend shell and static assets

The shell loads configuration once, checks ffmpeg in desktop mode and wraps every route in a `main` element.

## Facts
- `+layout.svelte` calls `appState.loadConfig()` in `onMount`, then in Tauri calls `invoke('check_prerequisites')` and stores `ffmpeg_available` in `appState.ffmpegAvailable` (src/routes/+layout.svelte).
- It shows an `error-banner` with install hints when `appState.ffmpegAvailable` is false (src/routes/+layout.svelte).
- `+layout.ts` and `widget/+layout.ts` export `ssr = false` and `prerender = true` (src/routes/+layout.ts, src/routes/widget/+layout.ts).
- `app.html` is the SvelteKit page template with `%sveltekit.head%` and `%sveltekit.body%` (src/app.html).
- `app.css` sets the dark page background `#0f172a` and font stack (src/app.css).
- `app.d.ts` declares an empty `App` namespace (src/app.d.ts).
- `src/lib/index.ts` holds a comment only (src/lib/index.ts).
- `favicon.svg` sits in `src/lib/assets` (src/lib/assets/favicon.svg).

## Uses
`$lib/state.svelte` (`appState`, `isTauri`); Tauri command `check_prerequisites`.

## Related

- [[building-blocks/frontend-state]]
- [[building-blocks/backend-ffmpeg]]
- [[interfaces/tauri-commands]]
