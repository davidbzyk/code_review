---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Configuration"
description: "Where application settings live and which modules read them."
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
  - resource: src-tauri/src/pipeline.rs
  - resource: src/routes/settings/+page.svelte
---
# Configuration

Settings are one `AppConfig` object stored as `config.json`.

## Facts
- Rust: `get_config` and `save_config` (src-tauri/src/config.rs); every field has a serde default so older files still load.
- Frontend: `appState.config` and `loadConfig`/`saveConfig` (src/lib/state.svelte.ts).
- Editors: src/routes/settings/+page.svelte (key, voices, Drive) and src/routes/+page.svelte (webcam, voice replacement, default voice).
- Readers: `process_recording` reads `output_dir`, `elevenlabs_api_key`, `voices` (src-tauri/src/pipeline.rs).

## Related
- [[building-blocks/config-store]]
- [[runtime/config-load-and-save]]
- [[interfaces/config-json-shape]]
