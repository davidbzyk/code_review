---
id: building-blocks/backend-elevenlabs
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend ElevenLabs client"
description: "Speech-to-speech upload and API key test against api.elevenlabs.io."
domain: architecture
tags:
  - building-block
  - backend
  - elevenlabs
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/elevenlabs.rs
relations:
  relates_to:
    - interfaces/external-http-apis
    - building-blocks/backend-pipeline
---

# Backend ElevenLabs client

`src-tauri/src/elevenlabs.rs` calls the ElevenLabs HTTP API with `reqwest`.

## Functions

- `speech_to_speech(api_key, voice_id, input_audio, output_audio)`: reads the WAV file, posts a multipart form (`audio` as `input.wav`, `model_id` `eleven_multilingual_sts_v2`, `remove_background_noise` `true`) to `https://api.elevenlabs.io/v1/speech-to-speech/<voice_id>?output_format=mp3_44100_128` with header `xi-api-key`, and writes the response bytes to `output_audio`. A non-success status returns `ElevenLabs API error <status>: <body>`.
- `test_api_key(api_key)` (async command): trims the key, returns `false` if empty, else `GET https://api.elevenlabs.io/v1/user` and returns whether the status is success.

Both log with the `log` crate under the `[elevenlabs]` prefix.

## Called by

`speech_to_speech` from `src-tauri/src/pipeline.rs`; `test_api_key` from `src/routes/settings/+page.svelte`.

## Related

- [interfaces/external-http-apis](../interfaces/external-http-apis.md)
- [building-blocks/backend-pipeline](./backend-pipeline.md)
- [crosscutting/logging](../crosscutting/logging.md)
