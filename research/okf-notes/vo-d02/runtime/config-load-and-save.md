---
id: runtime/config-load-and-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Runtime: load and save configuration
description: Order of config sources on load and the targets written on save.
domain: architecture
tags:
  - runtime
  - arc42-6
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/config.rs
  - resource: src/routes/+layout.svelte
related:
  - building-blocks/frontend-state-and-logging
  - building-blocks/backend-config
  - crosscutting/configuration-and-secrets
---

Configuration is loaded once at layout mount and saved from the settings page.

## Load
1. `onMount` in src/routes/+layout.svelte calls `appState.loadConfig()`.
2. Under Tauri, `get_config` is invoked (src-tauri/src/config.rs); on success the result is also stored in `localStorage` key `voiceover-config`.
3. Otherwise (browser, or Tauri failure) it fetches `/_config.json` and merges it over defaults.
4. Last, it reads `localStorage` `voiceover-config`; with nothing stored it logs "No config found" and keeps defaults.

## Save
1. `saveConfig()` writes `localStorage` first.
2. Under Tauri it invokes `save_config`, which writes `config.json` in the app data directory and calls `sync_to_static`.
3. `sync_to_static` writes `_config.json` into the first `static` directory found walking up from the executable, else `./static`.

Each step logs through `logger.configLoaded` or `logger.configSaved`; failures log `logger.error`.

## Related
[[building-blocks/frontend-state-and-logging]], [[building-blocks/backend-config]], [[crosscutting/configuration-and-secrets]]
