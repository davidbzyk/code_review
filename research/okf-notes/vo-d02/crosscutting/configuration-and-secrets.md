---
id: crosscutting/configuration-and-secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Configuration and secrets
description: Where settings and credentials are stored, and what is stripped when synced.
domain: architecture
tags:
  - crosscutting
  - arc42-8
  - config
  - secrets
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/backend-config
  - runtime/config-load-and-save
  - interfaces/config-data-shape
---

Settings live in one `AppConfig` object; credentials are fields inside it.

## Facts
- Desktop storage: `config.json` in `app_data_dir()` (src-tauri/src/config.rs).
- Browser and shared storage: `localStorage` key `voiceover-config` (src/lib/state.svelte.ts).
- Credential fields: `elevenlabs_api_key`, and in `google_drive`: `client_id`, `client_secret`, `access_token`, `refresh_token`.
- `sync_to_static` writes `_config.json` with those credential fields set to empty strings; it keeps voices, `output_dir`, `preferences`, Drive `email` and `connected`.
- The settings page shows the API key in a password input with a visibility toggle and logs only a masked key (src/routes/settings/+page.svelte).
- `test_api_key` logs the first six and last four characters (src-tauri/src/elevenlabs.rs).
- Drive scope is `drive.file` plus `email`; PKCE verifier and challenge protect the code exchange (src-tauri/src/google_drive.rs).
- `google_drive_disconnect` makes no change; the page clears token fields itself in `disconnectDrive()`.

## Used by
src-tauri/src/pipeline.rs (reads the key and voices), src/routes/preview/+page.svelte (reads tokens).

## Related
[[building-blocks/backend-config]], [[runtime/config-load-and-save]], [[interfaces/config-data-shape]]
