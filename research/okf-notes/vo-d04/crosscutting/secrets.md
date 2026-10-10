---
id: crosscutting/secrets
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Secrets and credentials"
description: "Where the API key and Google tokens are stored and sent."
domain: architecture
tags:
  - crosscutting
  - secrets
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: crosscutting
sources:
  - resource: src-tauri/src/config.rs
  - resource: src/lib/state.svelte.ts
  - resource: .gitignore
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
related:
  - crosscutting/configuration
  - building-blocks/backend-elevenlabs
  - building-blocks/backend-google-drive
---

# Secrets and credentials

The ElevenLabs key and Google client id, client secret and tokens are fields of `AppConfig`.

## Facts
- Stored in `config.json`, in `localStorage['voiceover-config']`, and (when the key is set) in `static/_config.json` (src-tauri/src/config.rs; src/lib/state.svelte.ts).
- `.gitignore` lists `static/_config.json` under "Config with secrets" (.gitignore).
- The key is sent in the `xi-api-key` header (src-tauri/src/elevenlabs.rs).
- Google access tokens are sent as bearer tokens; the PKCE verifier is random per connect (src-tauri/src/google_drive.rs).
- Settings masks the key input behind `apiKeyVisible` (src/routes/settings/+page.svelte).

## Related

- [[crosscutting/configuration]]
- [[building-blocks/backend-elevenlabs]]
- [[building-blocks/backend-google-drive]]
