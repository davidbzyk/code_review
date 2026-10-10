---
id: building-blocks/rust-secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Secrets"
description: "Keychain storage of API key and Google tokens through one JSON entry."
domain: architecture
tags:
  - building-blocks
  - rust
  - secrets
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/secrets.rs
relations:
  relates_to:
    - building-blocks/rust-config
    - crosscutting/secrets
---

The secrets module keeps four credentials in the operating system keychain through the `keyring` crate.

## Facts

- Constants `SERVICE = "com.voiceover.app"` and `ACCOUNT = "credentials"` name the single keychain entry (`src-tauri/src/secrets.rs`).
- The entry holds a JSON `Vault` with `elevenlabs_api_key`, `google_drive_client_secret`, `google_drive_access_token`, `google_drive_refresh_token`.
- `read_vault()` returns an empty `Vault` for `NoEntry`, and `None` on other keychain errors.
- `write_vault` serializes the vault and calls `set_password`; failures are logged with `log::error!`.
- `load_secrets(config)` copies each non-empty vault field into the `AppConfig`; it keeps the config unchanged when the keychain is unavailable.
- `save_secrets(config)` builds a vault from the config and writes it.
- `clear_secrets()` deletes the credential.
- `sanitize_config(config)` blanks the four secret fields.
- Callers: `src-tauri/src/config.rs` (`get_config`, `save_config`) and `src-tauri/src/google_drive.rs` (`google_drive_disconnect`).
- `src-tauri/Cargo.toml` enables the `apple-native` and `linux-native` features of `keyring`.

## Related

- [Rust config](rust-config.md)
- [Secrets concern](../crosscutting/secrets.md)
