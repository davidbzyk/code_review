---
id: runtime/config-load-and-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config load and save"
description: "Where config comes from at startup and where it is written."
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
  - resource: src-tauri/src/secrets.rs
  - resource: src/routes/+layout.svelte
related:
  - building-blocks/rust-config-and-secrets
  - crosscutting/configuration
  - crosscutting/secrets-handling
---
# Config load and save

Config is read once by the layout and written back whenever a page calls `saveConfig`.

## Load

1. `+layout.svelte` calls `appState.loadConfig()` on mount.
2. In Tauri, `loadConfig` invokes `get_config`; if the result has an ElevenLabs key it is used and mirrored to localStorage key `voiceover-config`.
3. `get_config` (src-tauri/src/config.rs) reads `<app data>/config.json`, or creates it from `static/_config.json` (debug builds) or defaults.
4. If `secrets_migrated` is false and any secret is present, it saves them to the keychain, rewrites the file without them and sets `secrets_migrated`.
5. It then overlays keychain values with `secrets::load_secrets`.
6. Otherwise `loadConfig` tries `fetch('/_config.json')`, then localStorage.

## Save

1. `saveConfig` writes a sanitized copy to localStorage, then invokes `save_config` in Tauri.
2. `save_config` calls `secrets::save_secrets`, writes the sanitized file, and in debug builds calls `sync_to_static`.

## Related

- [[building-blocks/rust-config-and-secrets]]
- [[crosscutting/configuration]]
- [[crosscutting/secrets-handling]]
