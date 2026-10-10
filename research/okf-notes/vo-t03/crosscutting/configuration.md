---
id: crosscutting/configuration
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Configuration"
description: "Where settings are defined, stored and read."
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
  - resource: src/routes/settings/+page.svelte
  - resource: vite.config.ts
related:
  - runtime/config-load-and-save
  - crosscutting/secrets-handling
  - building-blocks/rust-config-and-secrets
---
# Configuration

App settings are one `AppConfig` object, stored as `config.json` in the app data folder.

## Facts

- Fields: `elevenlabs_api_key`, `voices`, `output_dir`, `preferences`, `google_drive`, `secrets_migrated`, `provider`, `local_endpoint`, `local_voice_profile_id` (src-tauri/src/config.rs).
- Every field has a serde default, so older files load.
- `WebcamPosition` falls back to `bottom-right` for unknown strings (`deserialize_webcam_position`).
- The TypeScript mirror is `AppConfig` in src/lib/state.svelte.ts; `local_endpoint` is marked deprecated there.
- `isConfigured` is true for provider `local` with a profile id, or for ElevenLabs with a key and at least one voice.
- Browser mode keeps a sanitized copy in localStorage key `voiceover-config`.
- In debug builds the host also mirrors config to `static/_config.json`; `vite.config.ts` removes `_config.json` from production builds.
- The settings page edits voices, provider and Drive fields, then calls `saveConfig`.

## Used by

The layout, all routes, `pipeline.rs`.

## Related

- [[runtime/config-load-and-save]]
- [[crosscutting/secrets-handling]]
- [[building-blocks/rust-config-and-secrets]]
