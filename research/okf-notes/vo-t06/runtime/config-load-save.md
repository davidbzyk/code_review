---
id: runtime/config-load-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config Load and Save Flow"
description: "How configuration moves between the keychain, config.json, the static dev file and localStorage."
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
  - resource: src-tauri/src/secrets.rs
relations:
  relates_to:
    - building-blocks/rust-config
    - building-blocks/rust-secrets
    - crosscutting/configuration
---

Configuration is read at layout mount and written by `saveConfig()`.

## Load steps

1. `AppState.loadConfig()` (`src/lib/state.svelte.ts`): when `isTauri()`, `tauriInvoke('get_config')`.
2. `get_config` (`src-tauri/src/config.rs`) reads `config.json` or seeds it, migrates plaintext secrets to the keychain, then calls `secrets::load_secrets`.
3. If the returned `elevenlabs_api_key` is non-empty, the config is accepted and a sanitized copy goes to `localStorage` key `voiceover-config`.
4. Otherwise `fetch('/_config.json')` is tried; a file with an API key is merged, stored, and in Tauri sent back with `save_config`.
5. Last fallback: `localStorage`; with nothing stored, defaults stay.

## Save steps

1. `AppState.saveConfig()` writes the sanitized config to `localStorage`.
2. In Tauri it invokes `save_config`.
3. `save_config` calls `secrets::save_secrets`, writes the sanitized config to `config.json`, and in debug builds writes `static/_config.json`.

## Related

- [Rust config](../building-blocks/rust-config.md)
- [Rust secrets](../building-blocks/rust-secrets.md)
- [Configuration](../crosscutting/configuration.md)
