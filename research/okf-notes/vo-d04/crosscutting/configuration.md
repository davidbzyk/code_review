---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Configuration"
description: "Where settings live and which modules read them."
domain: architecture
tags:
  - crosscutting
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: crosscutting
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/tauri.conf.json
related:
  - runtime/config-load-save-flow
  - building-blocks/backend-config
  - crosscutting/secrets
---

# Configuration

Settings are one `AppConfig` object, stored as `config.json` in the app data directory and mirrored in `localStorage`.

## Facts
- Fields: `elevenlabs_api_key`, `voices`, `output_dir`, `preferences`, `google_drive` (src-tauri/src/config.rs; src/lib/state.svelte.ts).
- Defaults come from `AppConfig::default()` in Rust and the `AppState.config` initializer in TypeScript.
- Readers: src/routes/+page.svelte, src/routes/preview/+page.svelte, src/routes/settings/+page.svelte, src-tauri/src/pipeline.rs.
- Build-time settings are in src-tauri/tauri.conf.json (window, CSP, bundle).

## Related

- [[runtime/config-load-save-flow]]
- [[building-blocks/backend-config]]
- [[crosscutting/secrets]]
