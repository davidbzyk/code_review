---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: System context
description: VoiceOver is a desktop screen recorder that replaces the speaker's voice using ElevenLabs or a local TTS sidecar.
domain: architecture
tags:
  - context
  - boundary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/Info.plist
  - resource: package.json
related:
  - solution-strategy/technologies
  - building-blocks/tauri-core
  - building-blocks/sidecar-server
---

# System context

VoiceOver is a Tauri desktop application ("VoiceOver", identifier com.voiceover.app) that records the screen and microphone and can replace the recorded voice with a transformed voice (src-tauri/tauri.conf.json, src-tauri/Cargo.toml: "Screen recorder with ElevenLabs voice replacement").

## Boundary

- ElevenLabs API: speech-to-speech at `https://api.elevenlabs.io/v1/speech-to-speech` and key check at `/v1/user` (src-tauri/src/elevenlabs.rs).
- Google OAuth and Drive: `accounts.google.com`, `oauth2.googleapis.com`, `www.googleapis.com` (src-tauri/src/google_drive.rs, src/lib/drive.ts).
- ffmpeg and ffprobe binaries run as child processes (src-tauri/src/ffmpeg.rs).
- TTS sidecar: a Python FastAPI process on `127.0.0.1`, started by the Rust side (src-tauri/src/sidecar.rs, src-tauri/sidecar/server.py).
- HuggingFace model hosting, reached by the sidecar for model downloads (src-tauri/sidecar/server.py, `/models/download`).
- YouTube, reached by the sidecar through yt-dlp (src-tauri/sidecar/server.py, `/extract-youtube`).
- OS keychain via the `keyring` crate (src-tauri/src/secrets.rs).
- OS permissions declared for camera, microphone and screen capture (src-tauri/Info.plist).

## Users and entry points

- A person runs the desktop app: `main` calls `voiceover_lib::run()` (src-tauri/src/main.rs, src-tauri/src/lib.rs).
- Development entry: `pnpm dev` for the web UI on port 5170 and `tauri` commands from `@tauri-apps/cli` (package.json, src-tauri/tauri.conf.json).
- The same web UI also runs in a plain browser, where it calls ElevenLabs directly and uses ffmpeg.wasm (src/routes/preview/+page.svelte).

## Related

- [[solution-strategy/technologies]] - Technologies and structural decisions
- [[building-blocks/tauri-core]] - Tauri core
- [[building-blocks/sidecar-server]] - Sidecar server
