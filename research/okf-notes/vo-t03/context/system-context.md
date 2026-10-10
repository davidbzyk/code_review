---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "System context"
description: "What VoiceOver is, which external services and programs it calls, and the entry points a user starts."
domain: architecture
tags:
  - context
  - boundary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src/lib/drive.ts
  - resource: src-tauri/sidecar/server.py
  - resource: src/routes/+page.svelte
  - resource: src-tauri/sidecar/tts.py
related:
  - solution-strategy/technologies
  - building-blocks/tauri-host
  - interfaces/external-http-endpoints
---
# System context

VoiceOver is a Tauri desktop app (package `voiceover`, "Screen recorder with ElevenLabs voice replacement") that records the screen and microphone, then replaces the narrator voice using either ElevenLabs or a local TTS sidecar.

## Boundary list

- ElevenLabs speech-to-speech API, `https://api.elevenlabs.io/v1/speech-to-speech` and `/v1/user` (src-tauri/src/elevenlabs.rs; the browser path calls it directly from src/routes/preview/+page.svelte).
- Google OAuth and Drive endpoints: `accounts.google.com`, `oauth2.googleapis.com`, `www.googleapis.com` (src-tauri/src/google_drive.rs, src/lib/drive.ts).
- ffmpeg executable, bundled next to the main binary or found on PATH (src-tauri/src/ffmpeg.rs).
- Local TTS sidecar, a FastAPI process on `127.0.0.1` started by the host (src-tauri/src/sidecar.rs, src-tauri/sidecar/server.py).
- OS keychain via the `keyring` crate (src-tauri/src/secrets.rs).
- HuggingFace Hub model downloads and yt-dlp YouTube downloads, both run inside the sidecar (src-tauri/sidecar/server.py).
- The default web browser, opened for the Google consent page with `open::that` (src-tauri/src/google_drive.rs).

## Users and entry points

- A user starts the desktop app: `main()` calls `voiceover_lib::run()` (src-tauri/src/main.rs, src-tauri/src/lib.rs).
- The main window loads the SvelteKit root page, which records (src/routes/+page.svelte).
- A second window labelled `widget` can open at route `/widget` (src-tauri/src/commands/window.rs).
- The sidecar can also be started by hand with `python server.py --port ... --data-dir ... --parent-pid ...` (src-tauri/sidecar/server.py `main`).
- The frontend also runs in a plain browser; `isTauri()` selects the path (src/lib/state.svelte.ts).

## Related

- [[solution-strategy/technologies]]
- [[building-blocks/tauri-host]]
- [[interfaces/external-http-endpoints]]
