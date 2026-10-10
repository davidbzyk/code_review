---
id: runtime/config-load-and-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config Load and Save"
description: "How configuration moves between the Tauri file, the dev server file and localStorage."
domain: architecture
tags:
  - runtime
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/config.rs
---
# Config Load and Save

Load tries three sources in order; save writes to up to three places.

## Load steps (`loadConfig`, src/lib/state.svelte.ts)
1. If `isTauri()`, invoke `get_config` (`get_config` in src-tauri/src/config.rs reads or creates `config.json`), copy to `localStorage`, return.
2. Otherwise `fetch('/_config.json')`; on success merge into `config`.
3. Otherwise read `localStorage` key `voiceover-config`.

## Save steps (`saveConfig`)
1. Write `localStorage`.
2. If Tauri, invoke `save_config`; `save_config` writes `config.json` and calls `sync_to_static`, which writes `static/_config.json` when a `static` directory is found.

## Related
- [[building-blocks/config-store]]
- [[building-blocks/frontend-state]]
- [[crosscutting/configuration]]
