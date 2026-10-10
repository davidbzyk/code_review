---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Configuration
description: Where settings are defined, stored and read.
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
relations:
  relates_to:
    - runtime/config-load-and-save
    - crosscutting/secrets
    - building-blocks/rust-config-and-secrets
---
# Configuration

Settings are one `AppConfig` struct on the Rust side and an `AppConfig` type on the TypeScript side.

## Facts

- Fields: `elevenlabs_api_key`, `voices`, `output_dir`, `preferences`, `google_drive`, `secrets_migrated`, `provider`, `local_endpoint`, `local_voice_profile_id`, `local_tts_mode` (`src-tauri/src/config.rs`).
- Defaults: provider `elevenlabs`; `local_endpoint` `http://localhost:17493`; `output_dir` is the video dir plus `VoiceOver`.
- File: `config.json` in the Tauri app data dir (`config_path`).
- Browser fallback: `localStorage` key `voiceover-config` with secrets blanked (`sanitizeForStorage` in `src/lib/state.svelte.ts`).
- `local_endpoint` is marked deprecated in the TypeScript type; the sidecar uses a random port.
- Env var `ELEVENLABS_API_KEY` is read in `get_config`.
- Sidecar settings come from command-line flags (`main()` in `src-tauri/sidecar/server.py`).
- Dev server port 5170 (`vite.config.ts`).
- `static/_config.json` is read only in debug builds (`read_static_config`).

## Used by

`pipeline.rs`, `library.rs`, `src/routes/(app)/settings/+page.svelte`.

## Related

- [Flow: Config Load and Save](../runtime/config-load-and-save.md)
- [Secrets](secrets.md)
- [Rust Config and Secrets](../building-blocks/rust-config-and-secrets.md)
