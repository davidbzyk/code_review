---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "System Context"
description: "What VoiceOver is, the outside services and programs it calls, and the entry points a user starts."
domain: architecture
tags:
  - context
  - boundary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: docs/BUILD.md
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/main.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/config.rs
related:
  - solution-strategy/technology-choices
  - interfaces/external-http-apis
  - runtime/record-flow
---
# System Context

VoiceOver is a Tauri desktop app (also served as a browser page) that records the screen and microphone, replaces the voice through a text-to-speech provider, and saves or uploads the video.

## Boundary
- ElevenLabs HTTP API at https://api.elevenlabs.io (src-tauri/src/elevenlabs.rs; browser mode in src/routes/preview/+page.svelte).
- Voicebox local server, default endpoint http://localhost:17493 (src-tauri/src/config.rs `default_local_endpoint`; src-tauri/src/local_tts.rs).
- Google OAuth and Drive at accounts.google.com, oauth2.googleapis.com and www.googleapis.com (src-tauri/src/google_drive.rs).
- ffmpeg program, bundled sidecar or system PATH (src-tauri/src/ffmpeg.rs).
- Operating system keychain through the `keyring` crate (src-tauri/src/secrets.rs).
- Default web browser, opened for Google consent with `open::that` (src-tauri/src/google_drive.rs).

## Entry points
- `pnpm tauri dev` and `pnpm tauri build` start and package the desktop app (docs/BUILD.md).
- `pnpm dev` starts the Vite dev server (package.json).
- The Rust binary starts in `main` and calls `voiceover_lib::run()` (src-tauri/src/main.rs).
- The main window is 480 by 640 and labelled `main` (src-tauri/tauri.conf.json).

## Related
- [Technology Choices](../solution-strategy/technology-choices.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
- [Record Flow](../runtime/record-flow.md)
