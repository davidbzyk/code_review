---
id: building-blocks/frontend-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend shell"
description: "HTML template, global style, root layout and build configuration of the SvelteKit app."
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
  - resource: src/lib/index.ts
  - resource: src/routes/+layout.ts
  - resource: src/routes/widget/+layout.ts
  - resource: src/routes/+layout.svelte
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: tsconfig.json
relations:
  relates_to:
    - building-blocks/frontend-state
    - solution-strategy/technologies
---

# Frontend shell

The shell wraps every route: it supplies the HTML document, the dark global style, the root layout that loads config and checks ffmpeg, and the SvelteKit and Vite settings.

## Files and behaviour

- `src/app.html`: document with `%sveltekit.head%` and `%sveltekit.body%`; body sets `data-sveltekit-preload-data="hover"`.
- `src/app.css`: zero margins, `box-sizing: border-box`, background `#0f172a`, text `#f1f5f9`.
- `src/app.d.ts`: empty `App` namespace declarations.
- `src/lib/index.ts`: comment only; no exports.
- `src/routes/+layout.ts` and `src/routes/widget/+layout.ts`: both export `ssr = false` and `prerender = true`.
- `src/routes/+layout.svelte`: on mount calls `appState.loadConfig()`; when `isTauri()` it invokes `check_prerequisites` and stores `ffmpeg_available` in `appState.ffmpegAvailable`. It shows an error banner with install commands when ffmpeg is missing, then renders `children`.
- `svelte.config.js`: `@sveltejs/adapter-static` with `fallback: 'index.html'`; runes enabled for files outside `node_modules`.
- `vite.config.ts`: `sveltekit()` plugin, port 5170 with `strictPort`, `@ffmpeg/ffmpeg` and `@ffmpeg/util` excluded from `optimizeDeps`.
- `tsconfig.json`: extends `.svelte-kit/tsconfig.json`, `strict: true`.

## Uses

[frontend-state](frontend-state.md) for config and ffmpeg flag; the Rust command `check_prerequisites`.

## Related

- [building-blocks/frontend-state](./frontend-state.md)
- [building-blocks/backend-ffmpeg](./backend-ffmpeg.md)
- [solution-strategy/technologies](../solution-strategy/technologies.md)
- [runtime/load-config](../runtime/load-config.md)
