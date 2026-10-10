---
id: runtime/config-load-save-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config load and save flow"
description: "Order of config sources on load and the targets written on save."
domain: architecture
tags:
  - runtime
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/config.rs
related:
  - building-blocks/frontend-state
  - building-blocks/backend-config
  - crosscutting/configuration
---

# Config load and save flow

`appState.loadConfig()` tries three sources in order; `saveConfig()` writes to two places.

## Load steps
1. In Tauri, `loadConfig()` invokes `get_config`; the result is used only if `elevenlabs_api_key` is non-empty (src/lib/state.svelte.ts).
2. `get_config` reads `<app data dir>/config.json`, or seeds it from `static/_config.json` or defaults (src-tauri/src/config.rs).
3. Otherwise `fetch('/_config.json')` is tried; a result with an API key is merged, and in Tauri it is saved with `save_config` (src/lib/state.svelte.ts).
4. Otherwise `localStorage['voiceover-config']` is merged; if empty, defaults stay (src/lib/state.svelte.ts).

## Save steps
1. `saveConfig()` writes `localStorage` (src/lib/state.svelte.ts).
2. In Tauri it invokes `save_config`, which writes `config.json` and then calls `sync_to_static` (src-tauri/src/config.rs).
3. `sync_to_static` writes `static/_config.json` only when the API key is non-empty (src-tauri/src/config.rs).

## Related

- [[building-blocks/frontend-state]]
- [[building-blocks/backend-config]]
- [[crosscutting/configuration]]
