---
id: runtime/config-load-and-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config load and save flow"
description: "The frontend reads config from Tauri app data, then a synced static file, then localStorage, and writes to localStorage and Tauri."
domain: architecture
tags:
  - runtime
  - configuration
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/config.rs
  - resource: vite.config.ts
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/rust-config
    - crosscutting/configuration
---
# Config load and save flow

`loadConfig()` tries three sources in order and `saveConfig()` writes to two places.

## Load (`AppState.loadConfig`, src/lib/state.svelte.ts)

1. In Tauri, invoke `get_config`; if the result has an `elevenlabs_api_key`, set `config`, copy it to `localStorage` and return.
2. `get_config` (src-tauri/src/config.rs) reads `config.json` from the app data dir, or seeds it from `static/_config.json` or defaults.
3. Otherwise `fetch('/_config.json')`; if the JSON has a key, merge it into `config`, store it in `localStorage`, and in Tauri invoke `save_config` to persist it.
4. Otherwise read `localStorage` key `voiceover-config` and merge it; with nothing stored, log a warning and keep defaults.

## Save (`AppState.saveConfig`)

1. Write `config` to `localStorage`.
2. In Tauri invoke `save_config`, which writes `config.json` and calls `sync_to_static` (src-tauri/src/config.rs).

## Build note

`stripConfigPlugin` in vite.config.ts removes `build/_config.json` after a production bundle.

## Related

[[building-blocks/frontend-state]], [[building-blocks/rust-config]], [[crosscutting/configuration]]
