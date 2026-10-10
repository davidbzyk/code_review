---
id: glossary/terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Glossary"
description: "Terms used in the code, each with the file that defines it."
domain: architecture
tags:
  - glossary
  - arc42-12
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/lib/logger.ts
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/prerequisites.rs
relations:
  relates_to:
    - context/system-context
    - interfaces/tauri-commands
---

# Glossary

One line per term, with the defining file.

- `AppConfig`: persisted settings struct and type (`src-tauri/src/config.rs`, `src/lib/state.svelte.ts`).
- `appState`: shared runes state instance (`src/lib/state.svelte.ts`).
- `CaptureMode`: `fullscreen`, `window` or `region` (`src/lib/recorder.svelte.ts`).
- `DriveEvent`: Drive upload progress enum (`src-tauri/src/google_drive.rs`).
- `DriveTokens`: result of Drive sign-in (`src-tauri/src/google_drive.rs`).
- `isTauri`: desktop-mode test (`src/lib/state.svelte.ts`).
- `PipelineEvent`: processing progress enum (`src-tauri/src/pipeline.rs`).
- `PrerequisiteStatus`: ffmpeg availability result (`src-tauri/src/prerequisites.rs`).
- `RecordingState`: recording lifecycle union (`src/lib/state.svelte.ts`).
- S2S: speech-to-speech conversion, function `speech_to_speech` (`src-tauri/src/elevenlabs.rs`).
- Session id: `rec-<time>-<random>` name of one recording (`src/lib/recorder.svelte.ts`), checked by `validate_session_id` (`src-tauri/src/commands/recording.rs`).
- `Voice`: ElevenLabs voice entry with `is_default` (`src-tauri/src/config.rs`).
- Widget: the 340 by 80 `widget` window (`src-tauri/src/commands/window.rs`).
- `logger`: console logger object (`src/lib/logger.ts`).
- `normalize_to_mp4`, `extract_audio`, `replace_audio`: ffmpeg steps (`src-tauri/src/ffmpeg.rs`).
- `sync_to_static`: writes the secret-free `static/_config.json` (`src-tauri/src/config.rs`).

## Related

- [context/system-context](../context/system-context.md)
- [interfaces/tauri-commands](../interfaces/tauri-commands.md)
- [building-blocks/frontend-state](../building-blocks/frontend-state.md)
