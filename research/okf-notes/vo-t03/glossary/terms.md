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
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/voicebox.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/sidecar/tts.py
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/commands/recording.rs
related:
  - context/system-context
  - building-blocks/sidecar-engine
---
# Glossary

Terms as they appear in the code.

- S2S: speech-to-speech; `speech_to_speech` in src-tauri/src/elevenlabs.rs and src-tauri/src/local_tts.rs.
- Sidecar: the Python TTS process; `SidecarState` in src-tauri/src/sidecar.rs.
- Provider: `elevenlabs` or `local`; field `provider` in src-tauri/src/config.rs.
- Voice: an ElevenLabs voice entry; `Voice` in src-tauri/src/config.rs.
- Profile: a local voice profile folder; `create_profile` in src-tauri/sidecar/profiles.py.
- Sample: a reference WAV plus transcript in a profile; `add_sample` in src-tauri/sidecar/profiles.py.
- Voicebox: the name used for the sidecar client; `VoiceboxClient` in src/lib/voicebox.ts.
- Vault: the JSON blob stored in the keychain; `Vault` in src-tauri/src/secrets.rs.
- Session id: the name of a recording chunk folder; `validate_session_id` in src-tauri/src/commands/recording.rs.
- Chunk: a 5-second MediaRecorder fragment; `save_recording_chunk` in src-tauri/src/commands/recording.rs.
- Compositor: the canvas that crops regions and draws the webcam bubble; `startCompositorLoop` in src/lib/recorder.svelte.ts.
- Region: a cropped capture rectangle; `RegionRect` in src/lib/recorder.svelte.ts.
- Widget: the small recording window; `create_widget_window` in src-tauri/src/commands/window.rs.
- Generation: a queued TTS job; `_generations` in src-tauri/sidecar/server.py.
- Voice prompt: cloned voice data for Qwen; `create_voice_prompt` in src-tauri/sidecar/tts.py.
- PipelineEvent: progress message from Rust; src-tauri/src/pipeline.rs.
- DriveTokens: OAuth result; src-tauri/src/google_drive.rs.
- Watchdog: parent-process monitor; `_start_parent_watchdog` in src-tauri/sidecar/server.py.
- appState: shared reactive state object; src/lib/state.svelte.ts.

## Related

- [[context/system-context]]
- [[building-blocks/sidecar-engine]]
