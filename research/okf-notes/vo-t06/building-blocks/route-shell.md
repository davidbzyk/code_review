---
id: building-blocks/route-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Route Shell and Static Assets"
description: "Root layout, SvelteKit page options, HTML template, CSS and type declarations."
domain: architecture
tags:
  - building-blocks
  - frontend
  - sveltekit
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+layout.svelte
  - resource: src/routes/+layout.ts
  - resource: src/routes/widget/+layout.ts
  - resource: src/app.html
  - resource: src/app.css
  - resource: src/app.d.ts
relations:
  relates_to:
    - building-blocks/route-record
    - building-blocks/route-widget
    - solution-strategy/technologies
---

The shell files wrap the SvelteKit routes.

## Facts

- `src/routes/+layout.ts` and `src/routes/widget/+layout.ts` both export `ssr = false` and `prerender = true`.
- `src/routes/+layout.svelte` imports `../app.css`, and on mount calls `appState.loadConfig()`; when `isTauri()` it invokes `check_prerequisites` and stores `ffmpeg_available` in `appState.ffmpegAvailable`.
- The layout renders an error banner (text "ffmpeg not found." and install hints) when `appState.ffmpegAvailable` is false, then the page `children`.
- `src/app.html` is the page template with `%sveltekit.head%` and `%sveltekit.body%` and `data-sveltekit-preload-data="hover"` on the body.
- `src/app.css` sets margin, padding, system font stack, background `#0f172a`, text colour `#f1f5f9` and `box-sizing: border-box`.
- `src/app.d.ts` holds the empty `App` namespace declaration.
- `svelte.config.js` uses `@sveltejs/adapter-static` with `fallback: 'index.html'` and compiles non-`node_modules` files with runes.

## Related

- [Record route](route-record.md)
- [Widget route](route-widget.md)
- [Technologies](../solution-strategy/technologies.md)
