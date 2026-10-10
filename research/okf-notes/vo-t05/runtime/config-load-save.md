---
id: runtime/config-load-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Load and Save Config
description: How configuration moves between Tauri app data, the keychain, a dev static file and localStorage.
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
  - resource: src-tauri/src/secrets.rs
related:
  - building-blocks/rust-config-and-secrets
  - building-blocks/frontend-state-and-config
  - crosscutting/configuration
---

# Flow: Load and Save Config

Load trigger: `+layout.svelte` `onMount` calls `appState.loadConfig()`.

1. Under Tauri, `loadConfig` invokes `get_config` (src/lib/state.svelte.ts).
2. `get_config` (src-tauri/src/config.rs) reads `config.json`, or builds it from `read_static_config` or defaults and writes it.
3. If `secrets_migrated` is false and any secret field is set, it calls `save_secrets`, writes a sanitized file with `secrets_migrated = true`.
4. `load_secrets` fills the secret fields from the keychain vault.
5. If `elevenlabs_api_key` is set, the config is used; else `loadConfig` fetches `/_config.json`, then `localStorage` key `voiceover-config`.

Save trigger: `appState.saveConfig()`.

1. It writes a sanitized copy to `localStorage`.
2. Under Tauri it invokes `save_config`: `save_secrets`, `sanitize_config`, write `config.json`, and in debug builds `sync_to_static`.

## Related

- [Rust Config and Secrets](../building-blocks/rust-config-and-secrets.md)
- [Frontend State and Config](../building-blocks/frontend-state-and-config.md)
- [Configuration](../crosscutting/configuration.md)
