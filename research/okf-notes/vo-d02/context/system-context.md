---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: System context
description: What VoiceOver is, the external services it calls and the entry points a user starts.
domain: architecture
tags:
  - context
  - arc42-3
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: package.json
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
related:
  - solution-strategy/technology-choices
  - deployment/build-and-packaging
  - interfaces/external-http-apis
---

VoiceOver is a desktop screen recorder (Tauri 2 app, productName "VoiceOver") that records screen and microphone, optionally replaces the voice through ElevenLabs, and optionally uploads the result to Google Drive.

## Boundary
- ElevenLabs REST API, `https://api.elevenlabs.io`: speech-to-speech and key check (src-tauri/src/elevenlabs.rs; in browser mode src/routes/preview/+page.svelte and src/routes/settings/+page.svelte call it with `fetch`).
- Google OAuth and Drive APIs, `accounts.google.com`, `oauth2.googleapis.com`, `www.googleapis.com` (src-tauri/src/google_drive.rs; refresh and upload in browser mode in src/routes/preview/+page.svelte).
- `ffmpeg` program on the system PATH, run as a child process (src-tauri/src/ffmpeg.rs, src-tauri/src/prerequisites.rs).
- ffmpeg.wasm core files served from `/ffmpeg/` in browser mode (src/routes/preview/+page.svelte).
- The operating system: screen capture picker and microphone through `navigator.mediaDevices` (src/lib/recorder.svelte.ts), the default web browser opened for OAuth consent (`open::that` in src-tauri/src/google_drive.rs).
- The content security policy lists the allowed connect hosts (src-tauri/tauri.conf.json).

## Entry points
- `pnpm dev`, `pnpm build` (package.json); `beforeDevCommand` and `beforeBuildCommand` in src-tauri/tauri.conf.json run them for the desktop app.
- Rust `main()` calls `voiceover_lib::run()` (src-tauri/src/main.rs).
- The Vite dev server on port 5170 serves the same pages to a browser (vite.config.ts).
- Windows opened by the app: `main` (480 by 640) and `widget` (src-tauri/tauri.conf.json, src-tauri/src/commands/window.rs).

## Users
One local user who records, previews, processes and optionally shares a recording.

## Related
[[solution-strategy/technology-choices]], [[deployment/build-and-packaging]], [[interfaces/external-http-apis]]
