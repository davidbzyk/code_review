---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: System Context
description: What VoiceOver is, the external systems it calls, and the entry points a user starts.
domain: architecture
tags:
  - context
  - arc42
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src/lib/drive.ts
  - resource: src/lib/recorder.svelte.ts
relations:
  relates_to:
    - solution-strategy/technology-choices
    - building-blocks/rust-app-shell
    - deployment/build-and-packaging
---
# System Context

VoiceOver is a Tauri desktop app (productName "VoiceOver" in `src-tauri/tauri.conf.json`) that records the screen and replaces the recorded voice with a synthesized one, writing an MP4.

## Boundary

- ElevenLabs speech-to-speech API, `https://api.elevenlabs.io/v1/speech-to-speech` and `/v1/user` (`src-tauri/src/elevenlabs.rs`).
- Google OAuth and Drive: `accounts.google.com`, `oauth2.googleapis.com`, `www.googleapis.com` (`src-tauri/src/google_drive.rs`, `src/lib/drive.ts`).
- Local TTS sidecar, a Python process spawned on a random 127.0.0.1 port (`src-tauri/src/sidecar.rs`, `src-tauri/sidecar/server.py`).
- ffmpeg and ffprobe binaries run as child processes (`src-tauri/src/ffmpeg.rs`); the sidecar also runs ffmpeg (`src-tauri/sidecar/server.py`).
- YouTube, read by yt-dlp inside the sidecar route `/extract-youtube` (`src-tauri/sidecar/server.py`).
- Hugging Face model hub, read by `snapshot_download` in `/models/download` (`src-tauri/sidecar/server.py`).
- OS keychain through the `keyring` crate (`src-tauri/src/secrets.rs`).
- Screen, microphone and webcam capture through browser media APIs in the webview (`src/lib/recorder.svelte.ts`).

## Entry points

- `pnpm dev`, `pnpm build`, `pnpm test`, `pnpm check` (`package.json`).
- `voiceover_lib::run()` called from `fn main` (`src-tauri/src/main.rs`).
- The Tauri window labelled `main`, 900 by 640 (`src-tauri/tauri.conf.json`).
- `python server.py --port --data-dir --parent-pid` for the sidecar (`src-tauri/sidecar/server.py`).

## Related

- [Technology Choices](../solution-strategy/technology-choices.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
- [Build and Packaging](../deployment/build-and-packaging.md)
