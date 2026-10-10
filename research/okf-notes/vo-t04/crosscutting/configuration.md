---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Configuration"
description: "Settings live in config.json under app data, in localStorage, and in an ignored static/_config.json used by the dev server."
domain: architecture
tags:
  - crosscutting
  - configuration
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/config.rs
  - resource: vite.config.ts
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/pipeline.rs
relations:
  relates_to:
    - runtime/config-load-and-save
    - interfaces/config-schema
    - crosscutting/secrets-handling
---
# Configuration

Configuration is implemented in src/lib/state.svelte.ts and src-tauri/src/config.rs.

## Facts

- Stores: `<app_data_dir>/config.json` (Rust), `localStorage['voiceover-config']` (frontend), `static/_config.json` (written by `sync_to_static`, read by `fetch('/_config.json')`).
- docs/BUILD.md gives the macOS location `~/Library/Application Support/com.voiceover.app/config.json`; the identifier `com.voiceover.app` is in src-tauri/tauri.conf.json.
- `pipeline.rs` reads the output folder and ElevenLabs key through `config::get_config`.
- Build-time settings: ports and plugins in vite.config.ts, window and CSP in src-tauri/tauri.conf.json.
- No environment variable is read by the Rust or TypeScript sources in src and src-tauri/src that this note cites.

## Used by

src/routes/+layout.svelte, src/routes/settings/+page.svelte, src/routes/preview/+page.svelte, src-tauri/src/pipeline.rs.

## Related

[[runtime/config-load-and-save]], [[interfaces/config-schema]], [[crosscutting/secrets-handling]]
