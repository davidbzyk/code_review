---
id: building-blocks/frontend-shell
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend Shell"
description: "HTML template, global styles, route-level options and the root layout that loads configuration."
domain: architecture
tags:
  - building-block
  - svelte
  - layout
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/app.html
  - resource: src/app.css
  - resource: src/app.d.ts
  - resource: src/lib/index.ts
  - resource: src/routes/+layout.ts
  - resource: src/routes/+layout.svelte
  - resource: src/routes/widget/+layout.ts
---
# Frontend Shell

The shell supplies the page template, dark theme, route options and the startup check for config and ffmpeg.

## Facts
- src/app.html holds the `%sveltekit.head%` and `%sveltekit.body%` placeholders.
- src/app.css sets background `#0f172a`, text `#f1f5f9` and `box-sizing: border-box`.
- src/routes/+layout.ts and src/routes/widget/+layout.ts export `ssr = false` and `prerender = true`.
- src/routes/+layout.svelte calls `appState.loadConfig()` in `onMount`; in Tauri it also invokes `check_prerequisites` and sets `appState.ffmpegAvailable`. When false it renders an error banner with install commands.
- src/app.d.ts declares an empty `App` namespace; src/lib/index.ts holds only a comment.

## Related
- [[building-blocks/frontend-state]]
- [[building-blocks/home-screen]]
- [[crosscutting/dual-runtime-mode]]
