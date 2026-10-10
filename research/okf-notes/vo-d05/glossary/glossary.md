---
id: glossary/glossary
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Glossary
description: Terms used in the code with the file that defines each.
domain: architecture
tags:
  - glossary
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/sidecar.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/blobStore.ts
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
  - resource: src-tauri/sidecar/chunked_tts.py
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src/lib/voicebox.ts
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/src/local_tts.rs
related:
  - building-blocks/tauri-local-tts-bridge
  - interfaces/tauri-commands
  - interfaces/sidecar-http-routes
---

# Glossary

Terms, each with its defining file.

- Sidecar: the Python TTS server process (src-tauri/sidecar/server.py; state in src-tauri/src/sidecar.rs).
- `SidecarState`: managed state of child, port, data dir (src-tauri/src/sidecar.rs).
- `AppConfig`: persisted settings (src-tauri/src/config.rs; TypeScript type in src/lib/state.svelte.ts).
- `LocalTtsMode`: `tts` or `vc` (src-tauri/src/config.rs).
- Provider: `elevenlabs` or `local` (src-tauri/src/config.rs `default_provider`).
- S2S: speech-to-speech request (src-tauri/src/elevenlabs.rs `speech_to_speech`).
- VC: voice conversion through `/voice-convert` (src-tauri/src/local_tts.rs `voice_convert`).
- `PipelineEvent`: progress channel payload (src-tauri/src/pipeline.rs).
- `Vault`: JSON blob in the keychain (src-tauri/src/secrets.rs).
- `appState`: reactive UI store (src/lib/state.svelte.ts).
- `blobStore`: browser-mode blob holder (src/lib/blobStore.ts).
- `VoiceboxClient`: sidecar client class (src/lib/voicebox.ts).
- Voice profile: folder with `profile.json` and samples (src-tauri/sidecar/profiles.py).
- Sample: a reference WAV plus transcript text (src-tauri/sidecar/profiles.py `add_sample`).
- Generation: a queued TTS job keyed by uuid (src-tauri/sidecar/server.py `_generations`).
- Chunk: a 5 s recorder slice (src/lib/recorder.svelte.ts) or a text piece of up to 800 characters (src-tauri/sidecar/chunked_tts.py).
- Watchdog: parent-process monitor thread (src-tauri/sidecar/server.py `_start_parent_watchdog`).

## Related

- [[building-blocks/tauri-local-tts-bridge]] - Rust local TTS bridge
- [[interfaces/tauri-commands]] - Tauri commands
- [[interfaces/sidecar-http-routes]] - Sidecar HTTP routes
