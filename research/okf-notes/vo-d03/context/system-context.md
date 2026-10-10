---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "System context"
description: "What VoiceOver is, the external services it calls and the entry points a user starts."
domain: architecture
tags:
  - context
  - arc42-3
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
relations:
  relates_to:
    - solution-strategy/technologies
    - interfaces/external-http-apis
    - deployment/build-and-packaging
    - building-blocks/backend-entry
---

# System context

VoiceOver is a screen recorder, described in `src-tauri/Cargo.toml` as "Screen recorder with ElevenLabs voice replacement", that runs as a Tauri desktop app and also as a plain browser app.

## Boundary

| External party | Called from |
|---|---|
| ElevenLabs API `api.elevenlabs.io` (speech-to-speech, user info) | `src-tauri/src/elevenlabs.rs`; in browser mode `src/routes/preview/+page.svelte` and `src/routes/settings/+page.svelte` |
| Google OAuth `accounts.google.com`, `oauth2.googleapis.com` | `src-tauri/src/google_drive.rs`; browser-mode token refresh in `src/routes/preview/+page.svelte` |
| Google Drive and userinfo `www.googleapis.com` | `src-tauri/src/google_drive.rs`; `src/routes/preview/+page.svelte` |
| `ffmpeg` program on the system PATH | `src-tauri/src/ffmpeg.rs`, `src-tauri/src/prerequisites.rs` |
| ffmpeg.wasm core served from `/ffmpeg/` | `src/routes/preview/+page.svelte` |
| System browser (opened for Google consent) | `open::that` in `src-tauri/src/google_drive.rs` |
| Screen, microphone and webcam of the host | `navigator.mediaDevices` in `src/lib/recorder.svelte.ts` |

The allowed outbound hosts are listed in the `csp` value of `src-tauri/tauri.conf.json`.

## Entry points

- Desktop: `fn main` in `src-tauri/src/main.rs` calls `voiceover_lib::run()`.
- Dev server: `pnpm dev` runs `vite dev` on port 5170 (`package.json`, `vite.config.ts`).
- Routes: `/` record screen, `/preview`, `/settings`, `/widget` (`src/routes/`).

## Related

- [solution-strategy/technologies](../solution-strategy/technologies.md)
- [interfaces/external-http-apis](../interfaces/external-http-apis.md)
- [deployment/build-and-packaging](../deployment/build-and-packaging.md)
- [building-blocks/backend-entry](../building-blocks/backend-entry.md)
