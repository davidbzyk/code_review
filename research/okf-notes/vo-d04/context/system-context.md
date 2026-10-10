---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "System context"
description: "External services, programs and entry points around the VoiceOver desktop app."
domain: architecture
tags:
  - context
  - boundary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: context
sources:
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/lib/recorder.svelte.ts
  - resource: src/lib/state.svelte.ts
related:
  - solution-strategy/technologies
  - interfaces/external-http-apis
  - building-blocks/frontend-shell
  - building-blocks/backend-shell
---

# System context

VoiceOver is a screen recorder (Tauri window with a SvelteKit page set) that sends the recorded voice to ElevenLabs and writes an MP4 or WebM file.

## Boundary
- ElevenLabs API, `https://api.elevenlabs.io` (src-tauri/src/elevenlabs.rs; src/routes/preview/+page.svelte; src/routes/settings/+page.svelte)
- Google OAuth and Drive, `accounts.google.com`, `oauth2.googleapis.com`, `www.googleapis.com` (src-tauri/src/google_drive.rs; src/routes/preview/+page.svelte)
- `ffmpeg` program on the system PATH, started as a child process (src-tauri/src/ffmpeg.rs; src-tauri/src/prerequisites.rs)
- ffmpeg.wasm core files read from `/ffmpeg/` in browser mode (src/routes/preview/+page.svelte)
- Browser capture APIs `getDisplayMedia`, `getUserMedia`, `MediaRecorder` (src/lib/recorder.svelte.ts)
- The default web browser, opened for Google consent through the `open` crate (src-tauri/src/google_drive.rs)
- The local file system: the OS temp directory, the app data directory, the output folder (src-tauri/src/commands/recording.rs, src-tauri/src/config.rs, src-tauri/src/pipeline.rs)

## Entry points a user starts
- The desktop app: `main()` calls `voiceover_lib::run()` (src-tauri/src/main.rs, src-tauri/src/lib.rs); window "main", 480 by 640 (src-tauri/tauri.conf.json)
- The same pages in a browser served by Vite on port 5170 (vite.config.ts; src-tauri/tauri.conf.json `devUrl`)
- Routes `/`, `/preview`, `/settings`, `/widget` (src/routes)

## Related

- [[solution-strategy/technologies]]
- [[interfaces/external-http-apis]]
- [[building-blocks/frontend-shell]]
- [[building-blocks/backend-shell]]
