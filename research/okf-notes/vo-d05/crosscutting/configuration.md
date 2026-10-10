---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Configuration handling
description: Config lives in config.json in the app data folder, with a localStorage mirror and a dev-only static file.
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
  - resource: vite.config.ts
  - resource: src-tauri/src/pipeline.rs
related:
  - building-blocks/tauri-config-secrets
  - building-blocks/frontend-state
  - crosscutting/secrets
---

# Configuration handling

Configuration is one `AppConfig` shape on both sides (Rust `config::AppConfig`, TypeScript `AppConfig`).

## Facts

- Rust persists it to `config.json` under the Tauri `app_data_dir` (src-tauri/src/config.rs `config_path`).
- Serde defaults let missing fields load: `provider` `elevenlabs`, `local_tts_mode` `tts`, `output_dir` from `default_output_dir`.
- `WebcamPosition` falls back to `bottom-right` for unknown values (`deserialize_webcam_position`).
- The frontend loads config in `appState.loadConfig` and saves it in `saveConfig` (src/lib/state.svelte.ts).
- Debug builds mirror config to `static/_config.json`; the Vite plugin removes it from production builds (vite.config.ts).
- `pipeline.rs` reads `output_dir`, `provider`, `voices`, `local_voice_profile_id`, `local_tts_mode`.
- `local_endpoint` is kept in the type and marked deprecated in TypeScript.

## Related

- Secrets split: [[crosscutting/secrets]].

## Related

- [[building-blocks/tauri-config-secrets]] - Rust config and secrets
- [[building-blocks/frontend-state]] - Frontend state and Drive client
- [[crosscutting/secrets]] - Secret handling
