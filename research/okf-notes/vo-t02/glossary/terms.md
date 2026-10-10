---
id: glossary/terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Glossary"
description: "Terms used in the code, each with the file that defines it."
domain: architecture
tags:
  - glossary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/lib/voicebox.ts
  - resource: src/lib/drive.ts
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/src/tts_provider.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/local_tts.rs
related:
  - building-blocks/frontend-state
  - interfaces/events-and-channels
---
# Glossary

Each term below links to its defining file.

- `appState`: shared reactive state object (src/lib/state.svelte.ts).
- `RecordingState`: union of nine recording stages (src/lib/state.svelte.ts).
- `blobStore`: browser-mode Blob holder (src/lib/blobStore.ts).
- `CaptureMode`: `fullscreen`, `window` or `region` (src/lib/recorder.svelte.ts).
- `RegionRect`: x, y, width, height of a crop (src/lib/recorder.svelte.ts).
- `session_id`: id of one recording, shape `rec-<ms>-<random>` (src/lib/recorder.svelte.ts `generateSessionId`).
- chunk: one `chunk_NNNN.webm` piece (src-tauri/src/commands/recording.rs).
- `PipelineEvent`: progress message type (src-tauri/src/pipeline.rs).
- S2S: speech-to-speech (src-tauri/src/elevenlabs.rs).
- sidecar: bundled ffmpeg binary (src-tauri/src/ffmpeg.rs `resolve_ffmpeg_path`).
- `Vault`: keychain JSON of secrets (src-tauri/src/secrets.rs).
- `Provider`: `ElevenLabs` or `Local` (src-tauri/src/tts_provider.rs).
- Voicebox: local speech server client (src/lib/voicebox.ts).
- profile: Voicebox voice profile, `LocalVoice` (src-tauri/src/local_tts.rs).
- `DriveTokens`: Google token set (src-tauri/src/google_drive.rs).
- PKCE: verifier and challenge pair (src-tauri/src/google_drive.rs).
- `DriveUploadError`: upload error with status (src/lib/drive.ts).
- `WebcamPosition`: `bottom-left` or `bottom-right` (src-tauri/src/config.rs).

## Related
- [Frontend State](../building-blocks/frontend-state.md)
- [Events and Channels](../interfaces/events-and-channels.md)
