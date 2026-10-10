---
id: runtime/load-config
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Flow: load configuration at startup"
description: "Order of config sources tried by appState.loadConfig and the Rust get_config."
domain: architecture
tags:
  - runtime
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+layout.svelte
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/config.rs
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/backend-config
---

# Flow: load configuration at startup

Config loads once when the root layout mounts.

## Steps

1. `onMount` in `src/routes/+layout.svelte` awaits `appState.loadConfig()`.
2. If `isTauri()`, `loadConfig()` invokes `get_config`. `get_config` in `src-tauri/src/config.rs` reads `config.json` from the app data directory, or seeds it from `static/_config.json` or defaults.
3. If the returned `elevenlabs_api_key` is non-empty, it becomes `appState.config`, is copied to `localStorage` key `voiceover-config`, and loading stops.
4. Otherwise `loadConfig()` fetches `/_config.json`. A non-empty key there is merged into `config`, stored in `localStorage`, and in Tauri written back with `save_config`.
5. Otherwise it reads `localStorage` `voiceover-config` and merges it; with nothing stored it logs "No config found" and keeps defaults.
6. In Tauri the layout then invokes `check_prerequisites` and sets `appState.ffmpegAvailable`.

Saving goes the other way: `saveConfig()` writes `localStorage`, then invokes `save_config`, which writes `config.json` and runs `sync_to_static`.

## Related

- [building-blocks/frontend-state](../building-blocks/frontend-state.md)
- [building-blocks/backend-config](../building-blocks/backend-config.md)
- [crosscutting/configuration](../crosscutting/configuration.md)
