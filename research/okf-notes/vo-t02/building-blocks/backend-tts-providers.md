---
id: building-blocks/backend-tts-providers
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend TTS Providers"
description: "The ElevenLabs client, the Voicebox client and the provider enum."
domain: architecture
tags:
  - building-block
  - backend
  - tts
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/tts_provider.rs
related:
  - interfaces/external-http-apis
  - interfaces/tauri-commands-providers
  - runtime/process-recording-desktop
---
# Backend TTS Providers

This block sends extracted audio to a speech provider and saves the converted audio.

## src-tauri/src/elevenlabs.rs
Constants `S2S_BASE_URL`, `S2S_OUTPUT_FORMAT` (`mp3_44100_128`), `S2S_MODEL_ID` (`eleven_multilingual_sts_v2`), `API_KEY_HEADER` (`xi-api-key`), `USER_ENDPOINT`; `s2s_url`; `speech_to_speech`; command `test_api_key`.

## src-tauri/src/local_tts.rs
`speech_to_speech` (transcribe, generate, poll, download); commands `test_local_connection`, `list_local_voices`, `check_model_status`, `voicebox_fetch`, `voicebox_upload`; types `LocalVoice`, `ModelInfo`; `POLL_INTERVAL_MS = 500`, `POLL_TIMEOUT_SECS = 300`.

## src-tauri/src/tts_provider.rs
Enum `Provider` with `ElevenLabs` and `Local` and `as_str`. It is marked `#[allow(dead_code)]`; `pipeline.rs` compares `config.provider == "local"` as a string.

## Related
- [External HTTP APIs](../interfaces/external-http-apis.md)
- [Tauri Commands: Config, Providers and Drive](../interfaces/tauri-commands-providers.md)
- [Process Recording on Desktop](../runtime/process-recording-desktop.md)
