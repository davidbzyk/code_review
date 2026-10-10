---
id: context/system-context
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "System Context"
description: "VoiceOver is a desktop screen recorder that can replace the recorded voice through ElevenLabs."
domain: architecture
tags:
  - context
  - boundary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/tauri.conf.json
  - resource: package.json
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src/lib/tauri.ts
relations:
  relates_to:
    - solution-strategy/technologies
    - interfaces/external-http-apis
    - runtime/startup
---

The `description` in `src-tauri/Cargo.toml` is "Screen recorder with ElevenLabs voice replacement"; the product name in `src-tauri/tauri.conf.json` is `VoiceOver`.

## Boundary

| Outside party | How it is used | File |
|---|---|---|
| ElevenLabs API | speech-to-speech and key check | `src-tauri/src/elevenlabs.rs`, `src/routes/preview/+page.svelte` |
| Google OAuth and Drive APIs | sign-in, token, upload | `src-tauri/src/google_drive.rs`, `src/lib/drive.ts` |
| ffmpeg program | audio extraction, MP4 encoding | `src-tauri/src/ffmpeg.rs` |
| ffmpeg.wasm | browser-mode splicing | `src/routes/preview/+page.svelte` |
| Operating system keychain | secrets | `src-tauri/src/secrets.rs` |
| Default web browser | OAuth consent page | `src-tauri/src/google_drive.rs` |
| Screen, microphone, webcam | `getDisplayMedia`, `getUserMedia` | `src/lib/recorder.svelte.ts` |

## Entry points a user starts

- The desktop app: `pnpm tauri dev` or the packaged app (`docs/BUILD.md`).
- Browser mode: `pnpm dev` serves the SvelteKit app on port 5170 (`vite.config.ts`); the code branches on `isTauri()` (`src/lib/state.svelte.ts`).

## Related

- [Technologies](../solution-strategy/technologies.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
- [Application startup](../runtime/startup.md)
