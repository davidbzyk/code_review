---
id: building-blocks/rust-elevenlabs
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust ElevenLabs Client"
description: "HTTP client for the ElevenLabs speech-to-speech and user endpoints."
domain: architecture
tags:
  - building-blocks
  - rust
  - elevenlabs
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
relations:
  relates_to:
    - interfaces/external-http-apis
    - building-blocks/rust-pipeline
---

The ElevenLabs module sends extracted audio for voice conversion and checks API keys.

## Facts

- Constants: `S2S_BASE_URL` (`https://api.elevenlabs.io/v1/speech-to-speech`), `S2S_OUTPUT_FORMAT` (`mp3_44100_128`), `S2S_MODEL_ID` (`eleven_multilingual_sts_v2`), `API_KEY_HEADER` (`xi-api-key`), `USER_ENDPOINT` (`https://api.elevenlabs.io/v1/user`) (`src-tauri/src/elevenlabs.rs`).
- `s2s_url(voice_id)` formats `{S2S_BASE_URL}/{voice_id}?output_format={S2S_OUTPUT_FORMAT}`.
- `speech_to_speech(api_key, voice_id, input_audio, output_audio)` reads the WAV file, posts a multipart form with parts `audio`, `model_id` and `remove_background_noise=true`, and writes the response bytes to the output path. A non-success status becomes `Err("ElevenLabs API error {status}: {body}")`.
- `test_api_key(api_key)` is a Tauri command: it trims the key, returns `Ok(false)` for an empty key, sends a GET to `USER_ENDPOINT` and returns whether the status is success. The log line shows only the last four characters.
- Callers: `src-tauri/src/pipeline.rs` (`speech_to_speech`) and `src/routes/settings/+page.svelte` (`test_api_key`).

## Related

- [External HTTP APIs](../interfaces/external-http-apis.md)
- [Rust pipeline](rust-pipeline.md)
