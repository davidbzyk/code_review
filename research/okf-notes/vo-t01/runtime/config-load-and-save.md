---
id: runtime/config-load-and-save
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Config Load and Save
description: How settings and secrets are read and written.
domain: architecture
tags:
  - runtime
  - flow
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src/routes/+layout.svelte
relations:
  relates_to:
    - building-blocks/rust-config-and-secrets
    - building-blocks/frontend-state-and-ipc
    - crosscutting/configuration
---
# Flow: Config Load and Save

This flow runs when the root layout mounts and whenever settings change.

1. `onMount` in `src/routes/+layout.svelte` calls `appState.loadConfig()`.
2. In Tauri, `loadConfig` invokes `get_config`; the result is used when `elevenlabs_api_key` is non-empty.
3. `get_config` (`src-tauri/src/config.rs`) reads `config.json`, or creates it from defaults.
4. If `secrets_migrated` is false and secrets sit in the file, `save_secrets` moves them to the keychain and the file is rewritten without them.
5. `load_secrets` overlays keychain values.
6. When no key is set, `ELEVENLABS_API_KEY` from the environment fills in.
7. If the Tauri config has no key, `loadConfig` tries `/_config.json`, then `localStorage` key `voiceover-config`.
8. `saveConfig` writes sanitized JSON to `localStorage` and invokes `save_config`.
9. `save_config` calls `save_secrets`, `sanitize_config`, writes the file, and calls `sync_to_static`.

## Related

- [Rust Config and Secrets](../building-blocks/rust-config-and-secrets.md)
- [Frontend State and IPC](../building-blocks/frontend-state-and-ipc.md)
- [Configuration](../crosscutting/configuration.md)
