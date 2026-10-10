---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Configuration"
description: "Where settings live and which modules read them."
domain: architecture
tags:
  - crosscutting
  - configuration
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: vite.config.ts
  - resource: src-tauri/tauri.conf.json
  - resource: .gitignore
relations:
  relates_to:
    - runtime/config-load-save
    - crosscutting/secrets
    - building-blocks/rust-config
---

Settings are an `AppConfig` object shared by the Rust and TypeScript sides with the same field names.

## Facts

- Fields: `elevenlabs_api_key`, `voices`, `output_dir`, `preferences` (`default_capture_mode`, `webcam_enabled`, `voice_replacement_enabled`, `webcam_position`), `google_drive` (`src-tauri/src/config.rs`, `src/lib/state.svelte.ts`).
- Rust stores it at `<app data dir>/config.json` (`config_path`).
- The webview keeps a sanitized copy in `localStorage` under `voiceover-config`.
- In debug builds, Rust also reads and writes `static/_config.json`; the webview fetches `/_config.json` (`src/lib/state.svelte.ts`).
- `vite.config.ts` removes `build/_config.json` from production output.
- Readers: `pipeline.rs` (`output_dir`, `voices`, `elevenlabs_api_key`), settings and preview routes, `WebcamBubble.svelte` and `recorder.svelte.ts` (`webcam_position`), the record route (`webcam_enabled`).
- `.gitignore` lists `static/_config.json`.
- Build-time settings are in `src-tauri/tauri.conf.json`, `vite.config.ts` and `svelte.config.js`.

## Related

- [Config load and save flow](../runtime/config-load-save.md)
- [Secrets concern](secrets.md)
- [Rust config](../building-blocks/rust-config.md)
