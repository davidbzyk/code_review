---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "System context"
description: "VoiceOver is a Tauri desktop app with a browser mode that records a screen, swaps the voice through ElevenLabs and optionally uploads to Google Drive."
domain: architecture
tags:
  - context
  - boundary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/Info.plist
  - resource: static/robots.txt
  - resource: src-tauri/Cargo.toml
  - resource: src/lib/recorder.svelte.ts
relations:
  relates_to:
    - solution-strategy/technology-choices
    - interfaces/external-http-apis
    - deployment/build-and-package
---
# System context

VoiceOver ("Screen recorder with ElevenLabs voice replacement", src-tauri/Cargo.toml) records the screen and microphone, replaces the voice with an ElevenLabs voice, and saves or uploads the result.

## Boundary

| External party | Called from |
|---|---|
| ElevenLabs speech-to-speech and user endpoints, `https://api.elevenlabs.io` | src-tauri/src/elevenlabs.rs; src/routes/preview/+page.svelte and src/routes/settings/+page.svelte in browser mode |
| Google OAuth and Drive (`accounts.google.com`, `oauth2.googleapis.com`, `www.googleapis.com`) | src-tauri/src/google_drive.rs; src/routes/preview/+page.svelte |
| ffmpeg binary (bundled sidecar `binaries/ffmpeg`, or `ffmpeg` on PATH) | src-tauri/src/ffmpeg.rs, src-tauri/src/prerequisites.rs |
| ffmpeg.wasm core served from `/ffmpeg/` | src/routes/preview/+page.svelte |
| Operating system: screen capture, microphone, camera (usage strings) | src-tauri/Info.plist; src/lib/recorder.svelte.ts |
| Default browser, opened for Google consent | src-tauri/src/google_drive.rs (`open::that`) |

The content security policy that lists the permitted network hosts is in src-tauri/tauri.conf.json.

## Users and entry points

- Desktop: `main` calls `voiceover_lib::run()` (src-tauri/src/main.rs); the main window is 480 by 640 (src-tauri/tauri.conf.json).
- Browser: `pnpm dev` serves the SvelteKit app on port 5170 (package.json, vite.config.ts).
- Routes: `/`, `/preview`, `/settings`, `/widget` (src/routes).
- src-tauri/capabilities/default.json grants the windows `main` and `widget` their permissions.

## Related

[[solution-strategy/technology-choices]], [[interfaces/external-http-apis]], [[deployment/build-and-package]]
