---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "System Context"
description: "What VoiceOver is, which outside services it calls, and which entry points a user starts."
domain: architecture
tags:
  - context
  - boundary
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
---
# System Context

VoiceOver is a Tauri desktop screen recorder that replaces the recorded voice with an ElevenLabs voice (src-tauri/Cargo.toml: description "Screen recorder with ElevenLabs voice replacement").

## Boundary list
- ElevenLabs HTTP API, `https://api.elevenlabs.io/v1/speech-to-speech/{voice}` and `/v1/user` (src-tauri/src/elevenlabs.rs; also called with `fetch` from src/routes/preview/+page.svelte and src/routes/settings/+page.svelte).
- Google OAuth and Drive APIs: `accounts.google.com`, `oauth2.googleapis.com/token`, `www.googleapis.com` (src-tauri/src/google_drive.rs; refresh and upload in src/routes/preview/+page.svelte).
- The `ffmpeg` program on the system PATH, run as a child process (src-tauri/src/ffmpeg.rs, src-tauri/src/prerequisites.rs).
- ffmpeg.wasm in the browser path, loaded from `/ffmpeg/` (src/routes/preview/+page.svelte).
- The operating system browser, opened with `open::that` for Google consent (src-tauri/src/google_drive.rs).
- Browser media APIs `getDisplayMedia` and `getUserMedia` (src/lib/recorder.svelte.ts).

## Entry points a user starts
- Desktop app: `fn main` calls `voiceover_lib::run()` (src-tauri/src/main.rs).
- Browser dev server: `vite dev` on port 5170 (package.json, vite.config.ts).
- Windows opened by the app: `main` (src-tauri/tauri.conf.json) and `widget` (src-tauri/src/commands/window.rs).

## Related
- [[solution-strategy/technology-choices]]
- [[interfaces/external-http-apis]]
- [[deployment/build-and-packaging]]
