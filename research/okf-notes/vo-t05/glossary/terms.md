---
id: glossary/terms
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
  - resource: src/lib/state.svelte.ts
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/tts_provider.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/chunked_tts.py
  - resource: src-tauri/sidecar/profiles.py
  - resource: src/lib/blobStore.ts
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/secrets.rs
related:
  - context/system-context
  - building-blocks/sidecar-engine
  - building-blocks/rust-tts-providers
---

# Glossary

- `appState`: the shared reactive state object (src/lib/state.svelte.ts).
- `RecordingState`: nine UI states from `ready` to `saved` (src/lib/state.svelte.ts).
- `blobStore`: in-memory video and audio blobs (src/lib/blobStore.ts).
- `VoiceboxClient`: sidecar client class (src/lib/voicebox.ts).
- sidecar: the Python child process (src-tauri/src/sidecar.rs, src-tauri/sidecar/server.py).
- `SidecarState`: managed state for the child (src-tauri/src/sidecar.rs).
- `PipelineEvent`: progress messages from `process_recording` (src-tauri/src/pipeline.rs).
- `Provider`: `elevenlabs` or `local` (src-tauri/src/tts_provider.rs).
- `LocalTtsMode`: `tts` or `vc` (src-tauri/src/config.rs).
- S2S: speech-to-speech, `speech_to_speech` functions (src-tauri/src/elevenlabs.rs, src-tauri/src/local_tts.rs).
- VC: voice conversion, `/voice-convert` (src-tauri/sidecar/server.py).
- profile: a named voice with samples (src-tauri/sidecar/profiles.py).
- sample: one WAV plus reference text in a profile (src-tauri/sidecar/profiles.py `add_sample`).
- generation: a queued TTS or VC job with an id (`_generations` in server.py).
- segment: a timed phrase from `transcribe` (src-tauri/sidecar/tts.py).
- chunk: either a 5-second recording piece or a text piece up to 800 chars (src/lib/recorder.svelte.ts, src-tauri/sidecar/chunked_tts.py).
- `Vault`: JSON struct stored in the keychain (src-tauri/src/secrets.rs).
- `DriveTokens`: OAuth result (src-tauri/src/google_drive.rs).
- `ALLOWED_SIDECAR_PATHS`: proxy allowlist (src-tauri/src/local_tts.rs).
- watchdog: parent-PID monitor thread (src-tauri/sidecar/server.py).

## Related

- [System Context](../context/system-context.md)
- [Sidecar Engine Modules](../building-blocks/sidecar-engine.md)
- [Rust TTS Providers and Models](../building-blocks/rust-tts-providers.md)
