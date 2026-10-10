---
id: glossary/glossary
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Glossary
description: Terms used in the code, each with the file that defines it.
domain: architecture
tags:
  - glossary
  - arc42
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/sidecar/chunked_tts.py
  - resource: src/lib/blobStore.ts
  - resource: src-tauri/src/library.rs
  - resource: src-tauri/src/tts_provider.rs
relations:
  relates_to:
    - context/system-context
    - building-blocks/rust-local-tts-and-sidecar
---
# Glossary

Each line gives a term and its defining file.

- Sidecar: the Python TTS process; `SidecarState` in `src-tauri/src/sidecar.rs`.
- HttpClient: shared reqwest client; `src-tauri/src/local_tts.rs`.
- Provider: `elevenlabs` or `local`; `src-tauri/src/tts_provider.rs`, `provider` field in `src-tauri/src/config.rs`.
- LocalTtsMode: `tts` or `vc`; `src-tauri/src/config.rs`.
- Vault: keychain JSON record; `src-tauri/src/secrets.rs`.
- PipelineEvent: progress message from `process_recording`; `src-tauri/src/pipeline.rs`.
- RecordingMeta: contents of `.meta.json`; `src-tauri/src/library.rs`.
- RecordingState: nine UI states; `src/lib/state.svelte.ts`.
- appState: global reactive state; `src/lib/state.svelte.ts`.
- blobStore: browser-mode blob holder; `src/lib/blobStore.ts`.
- VoiceboxClient: sidecar client class; `src/lib/voicebox.ts`.
- Profile: a named voice with samples; `src-tauri/sidecar/profiles.py`.
- Generation: one queued audio job with an id; `_generations` in `src-tauri/sidecar/server.py`.
- Segment: a timed phrase from Whisper; `_group_words_into_phrases` in `src-tauri/sidecar/tts.py`.
- Chunk: a piece of text or audio; `split_text_into_chunks` in `src-tauri/sidecar/chunked_tts.py`.
- Watchdog: thread that exits the sidecar when its parent dies; `_start_parent_watchdog` in `src-tauri/sidecar/server.py`.
- Widget: the small always-on-top recording window; `src-tauri/src/commands/window.rs`.

## Related

- [System Context](../context/system-context.md)
- [Rust Local TTS and Sidecar Manager](../building-blocks/rust-local-tts-and-sidecar.md)
