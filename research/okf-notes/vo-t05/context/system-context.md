---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: System Context
description: What VoiceOver is, the external services and programs it calls, and the entry points a user starts.
domain: architecture
tags:
  - context
  - arc42
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/tauri.conf.json
  - resource: package.json
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/sidecar/server.py
related:
  - solution-strategy/technology-choices
  - interfaces/external-http-apis
  - building-blocks/rust-app-shell
---

# System Context

VoiceOver is a desktop screen recorder (Tauri app, product name "VoiceOver") that records the screen and microphone and can replace the recorded voice with a synthesized voice (src-tauri/Cargo.toml description: "Screen recorder with ElevenLabs voice replacement").

## Boundary list

| External party | How it is reached | File |
|---|---|---|
| ElevenLabs speech-to-speech API | HTTPS POST, `xi-api-key` header | src-tauri/src/elevenlabs.rs |
| Google OAuth and Drive APIs | browser consent, loopback callback, HTTPS upload | src-tauri/src/google_drive.rs |
| ffmpeg and ffprobe programs | child processes | src-tauri/src/ffmpeg.rs |
| Python TTS sidecar | child process plus HTTP on 127.0.0.1 | src-tauri/src/sidecar.rs |
| macOS keychain (service `com.voiceover.app`) | `keyring` crate | src-tauri/src/secrets.rs |
| HuggingFace model hub | `snapshot_download` inside the sidecar | src-tauri/sidecar/server.py |
| YouTube | `yt_dlp` inside the sidecar | src-tauri/sidecar/server.py |
| Screen, microphone, webcam | `getDisplayMedia`, `getUserMedia` | src/lib/recorder.svelte.ts |

## Entry points

- Desktop app: `main()` calls `voiceover_lib::run()` (src-tauri/src/main.rs, src-tauri/src/lib.rs).
- Window "main", 480 by 640 (src-tauri/tauri.conf.json); routes `/`, `/settings`, `/create-voice`, `/preview`, `/widget` (src/routes).
- Dev: `pnpm dev` on port 5170 (package.json, vite.config.ts).
- Sidecar, started by the app: `python server.py --port --data-dir --parent-pid` (src-tauri/sidecar/server.py `main`).

## Related

- [Technology Choices](../solution-strategy/technology-choices.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
