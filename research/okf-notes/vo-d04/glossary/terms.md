---
id: glossary/terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Glossary"
description: "Terms used in the code with their defining files."
domain: architecture
tags:
  - glossary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: glossary
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/elevenlabs.rs
related:
  - interfaces/tauri-commands
  - building-blocks/frontend-state
---

# Glossary

One line per term.

- `appState`: shared runes state instance (src/lib/state.svelte.ts)
- `AppConfig`: persisted settings struct (src-tauri/src/config.rs; type in src/lib/state.svelte.ts)
- `RecordingState`: UI phase union (src/lib/state.svelte.ts)
- `isTauri`: desktop-mode test (src/lib/state.svelte.ts)
- `CaptureMode`: `fullscreen`, `window`, `region` (src/lib/recorder.svelte.ts)
- `session_id`: folder name for chunks (src-tauri/src/commands/recording.rs)
- `chunk`: one MediaRecorder data piece saved as `chunk_NNNN.webm` (src-tauri/src/commands/recording.rs)
- `PipelineEvent`: progress message enum (src-tauri/src/pipeline.rs)
- `DriveEvent`, `DriveTokens`: Drive messages and token set (src-tauri/src/google_drive.rs)
- `S2S`: ElevenLabs speech-to-speech, `speech_to_speech` (src-tauri/src/elevenlabs.rs)
- `Voice`: id, name, description, is_default (src-tauri/src/config.rs)
- `widget`: label of the small recording window (src-tauri/src/commands/window.rs)
- `PKCE`: code verifier and S256 challenge (src-tauri/src/google_drive.rs)

## Related

- [[interfaces/tauri-commands]]
- [[building-blocks/frontend-state]]
