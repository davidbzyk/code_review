---
id: crosscutting/dual-runtime-mode
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Dual Runtime Mode"
description: "The same frontend runs inside Tauri or in a plain browser."
domain: architecture
tags:
  - crosscutting
  - tauri
  - browser
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/+layout.svelte
---
# Dual Runtime Mode

A check for `window.__TAURI_INTERNALS__` selects the Tauri or browser branch.

## Facts
- `isTauri()` is defined separately in src/lib/state.svelte.ts, src/lib/recorder.svelte.ts, src/routes/+page.svelte, src/routes/preview/+page.svelte and src/routes/settings/+page.svelte; src/routes/+layout.svelte uses a constant.
- Tauri APIs load by dynamic `import('@tauri-apps/api/core')`.
- Differences: chunk storage, processing, Drive upload and Drive connect (browser shows a message).

## Related
- [[solution-strategy/technology-choices]]
- [[runtime/process-recording-desktop]]
- [[runtime/process-recording-browser]]
