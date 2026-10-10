---
id: runtime/config-load-and-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config Load and Save"
description: "How configuration moves between the webview, localStorage, config.json and the keychain."
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
related:
  - building-blocks/backend-config-and-secrets
  - crosscutting/configuration
  - crosscutting/secrets
---
# Config Load and Save

`AppState.loadConfig` and `saveConfig` call the Rust commands `get_config` and `save_config`.

## Load
1. `loadConfig` (src/lib/state.svelte.ts) under Tauri invokes `get_config`; it keeps the result when `elevenlabs_api_key` is non-empty.
2. `get_config` (src-tauri/src/config.rs) reads `config.json` in the app data directory, or creates it from `read_static_config` or defaults.
3. If `secrets_migrated` is false and secret fields are set, it calls `save_secrets`, writes a sanitized file and sets `secrets_migrated`.
4. It calls `load_secrets` to fill secrets from the keychain.
5. Otherwise `loadConfig` fetches `/_config.json`, then falls back to localStorage key `voiceover-config`.

## Save
1. `saveConfig` writes a sanitized copy to localStorage.
2. Under Tauri it invokes `save_config`, which calls `save_secrets`, writes the sanitized `config.json`, and calls `sync_to_static` (debug builds only).

## Related
- [Backend Config and Secrets](../building-blocks/backend-config-and-secrets.md)
- [Configuration](../crosscutting/configuration.md)
- [Secrets](../crosscutting/secrets.md)
