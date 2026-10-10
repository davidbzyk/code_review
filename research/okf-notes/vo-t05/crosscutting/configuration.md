---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Configuration
description: Where settings are defined, stored and read across the layers.
domain: architecture
tags:
  - crosscutting
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/tauri.conf.json
  - resource: vite.config.ts
  - resource: src-tauri/sidecar/server.py
related:
  - building-blocks/rust-config-and-secrets
  - runtime/config-load-save
  - crosscutting/secrets
---

# Configuration

Application settings are one `AppConfig` record, mirrored in Rust and TypeScript.

## Facts

- Rust type `AppConfig` (src-tauri/src/config.rs) and TypeScript type `AppConfig` (src/lib/state.svelte.ts) carry the same field names.
- Serde `#[serde(default)]` supplies defaults for missing fields; `default_output_dir` is `<videos or home>/VoiceOver`.
- `preferences` holds `default_capture_mode`, `webcam_enabled`, `voice_replacement_enabled`, `webcam_position`.
- `local_endpoint` is marked deprecated in the TypeScript type.
- `get_config` and `save_config` read and write `config.json` in the app data dir (`config_path`).
- The sidecar takes its settings from command-line arguments (`main` in server.py) and sets `HF_HUB_CACHE`.
- Tauri settings (window, CSP, bundle) are in src-tauri/tauri.conf.json; Vite settings in vite.config.ts.
- Hard-coded constants: sidecar health timeout 60 s (src-tauri/src/sidecar.rs), local poll timeout 300 s (src-tauri/src/local_tts.rs).

## Used by

`pipeline.rs`, `settings` route, `+page.svelte`, `preview` route.

## Related

- [Rust Config and Secrets](../building-blocks/rust-config-and-secrets.md)
- [Flow: Load and Save Config](../runtime/config-load-save.md)
- [Secrets](./secrets.md)
