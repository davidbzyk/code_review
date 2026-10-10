---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Configuration"
description: "Where settings live: config.json, localStorage, static/_config.json and build config files."
domain: architecture
tags:
  - crosscutting
  - config
  - arc42-8
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: src/routes/settings/+page.svelte
  - resource: svelte.config.js
  - resource: vite.config.ts
relations:
  relates_to:
    - runtime/load-config
    - building-blocks/backend-config
---

# Configuration

User settings are one `AppConfig` object stored in up to three places.

## Locations

- Desktop store: `config.json` in the Tauri app data directory (`config_path` in `src-tauri/src/config.rs`).
- Browser store: `localStorage` key `voiceover-config` (`src/lib/state.svelte.ts`).
- Seed and dev bridge: `static/_config.json`, read by `read_static_config` and written by `sync_to_static`; the frontend fetches it as `/_config.json`.

## Contents

API key, voice list, `output_dir`, `preferences` (capture mode, webcam, voice replacement) and Google Drive fields (`src-tauri/src/config.rs`, mirrored by the types in `src/lib/state.svelte.ts`).

## Editing

`src/routes/settings/+page.svelte` edits `appState.config` and calls `saveConfig()`; `src/routes/+page.svelte` toggles preferences in place.

## Build-time settings

`svelte.config.js` (adapter and runes) and `vite.config.ts` (port 5170).

## Users

`pipeline.rs` reads the config for `output_dir`, the key and voices.

## Related

- [runtime/load-config](../runtime/load-config.md)
- [building-blocks/backend-config](../building-blocks/backend-config.md)
- [building-blocks/frontend-state](../building-blocks/frontend-state.md)
- [crosscutting/secrets](./secrets.md)
