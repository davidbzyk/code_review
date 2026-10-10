---
id: glossary/terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Glossary
description: Terms used in the code with the file that defines each.
domain: architecture
tags:
  - glossary
  - arc42-12
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/config.rs
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src/lib/logger.ts
related:
  - context/system-context
  - interfaces/tauri-commands
---

Each line gives a term and the file that defines it.

- `appState`: the shared state singleton (src/lib/state.svelte.ts).
- `AppConfig`: persisted settings (src-tauri/src/config.rs, src/lib/state.svelte.ts).
- `RecordingState`: lifecycle values `ready` to `saved` (src/lib/state.svelte.ts).
- `isTauri`: desktop detection (src/lib/state.svelte.ts).
- `CaptureMode`: `fullscreen`, `window`, `region` (src/lib/recorder.svelte.ts).
- session id: name of a recording's temp folder (src-tauri/src/commands/recording.rs, src/lib/recorder.svelte.ts).
- chunk: one-second `MediaRecorder` blob saved as `chunk_NNNN.webm` (src-tauri/src/commands/recording.rs).
- widget: the small always-on-top window (src-tauri/src/commands/window.rs).
- `PipelineEvent`: progress messages of `process_recording` (src-tauri/src/pipeline.rs).
- `DriveEvent`: progress messages of `upload_to_drive` (src-tauri/src/google_drive.rs).
- `DriveTokens`: OAuth result (src-tauri/src/google_drive.rs).
- S2S: ElevenLabs speech-to-speech, `speech_to_speech` (src-tauri/src/elevenlabs.rs).
- voice replacement: preference `voice_replacement_enabled` (src-tauri/src/config.rs).
- `sync_to_static`: writes the sanitised `_config.json` (src-tauri/src/config.rs).
- `logger`: console logger with `[VO:` prefix (src/lib/logger.ts).

## Related
[[context/system-context]], [[interfaces/tauri-commands]]
