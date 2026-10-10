---
id: building-blocks/rust-elevenlabs
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust ElevenLabs client"
description: "elevenlabs.rs sends audio to the ElevenLabs speech-to-speech endpoint and validates API keys."
domain: architecture
tags:
  - building-block
  - rust
  - elevenlabs
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
relations:
  relates_to:
    - building-blocks/rust-media-pipeline
    - interfaces/external-http-apis
    - crosscutting/secrets-handling
---
# Rust ElevenLabs client

The ElevenLabs client holds the API constants and two network calls (src-tauri/src/elevenlabs.rs).

## Constants

`S2S_BASE_URL` (`https://api.elevenlabs.io/v1/speech-to-speech`), `S2S_OUTPUT_FORMAT` (`mp3_44100_128`), `S2S_MODEL_ID` (`eleven_multilingual_sts_v2`), `API_KEY_HEADER` (`xi-api-key`), `USER_ENDPOINT` (`https://api.elevenlabs.io/v1/user`).

## Functions

- `s2s_url(voice_id)`: base URL plus voice id plus `?output_format=...`.
- `speech_to_speech(api_key, voice_id, input_audio, output_audio)`: reads the WAV, posts a multipart form (`audio`, `model_id`, `remove_background_noise=true`), logs size and timing, writes the response bytes to `output_audio`; a non-success status returns `ElevenLabs API error <status>: <body>`.
- `test_api_key(api_key)` (command): trims the key, returns `Ok(false)` if empty, otherwise GETs `USER_ENDPOINT` and returns whether the status is success.

## Called by

src-tauri/src/pipeline.rs (`speech_to_speech`); src/routes/settings/+page.svelte (`test_api_key`).

## Related

[[building-blocks/rust-media-pipeline]], [[interfaces/external-http-apis]], [[crosscutting/secrets-handling]]
