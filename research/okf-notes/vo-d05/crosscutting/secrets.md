---
id: crosscutting/secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Secret handling
description: API key and Drive tokens are kept in the OS keychain and stripped from files and localStorage.
domain: architecture
tags:
  - crosscutting
  - security
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/sidecar/server.py
related:
  - building-blocks/tauri-config-secrets
  - crosscutting/configuration
  - crosscutting/error-handling
---

# Secret handling

Secrets are never written to the config file by the save path.

## Facts

- `save_secrets` writes one JSON `Vault` into the keychain entry `com.voiceover.app` / `credentials` (src-tauri/src/secrets.rs).
- `sanitize_config` empties the key, client secret and tokens before `config.json` is written (src-tauri/src/config.rs `save_config`).
- `get_config` moves plaintext secrets from an older file into the keychain once and sets `secrets_migrated`.
- The frontend `sanitizeForStorage` blanks the same fields before `localStorage` (src/lib/state.svelte.ts).
- `google_drive_disconnect` clears the keychain entry.
- OAuth uses PKCE with a random `state` check (src-tauri/src/google_drive.rs); uploaded files stay private, with a comment noting no automatic sharing.
- Path guards: `validate_session_id` and the `read_file_bytes` allowlist (src-tauri/src/commands/recording.rs); `_validate_path` in the sidecar (src-tauri/sidecar/server.py).

## Related

- [[building-blocks/tauri-config-secrets]] - Rust config and secrets
- [[crosscutting/configuration]] - Configuration handling
- [[crosscutting/error-handling]] - Error handling
