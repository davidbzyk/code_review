---
id: building-blocks/backend-elevenlabs
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend ElevenLabs client"
description: "Speech-to-speech request and API key test against api.elevenlabs.io."
domain: architecture
tags:
  - backend
  - elevenlabs
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/elevenlabs.rs
related:
  - building-blocks/backend-pipeline
  - interfaces/external-http-apis
  - crosscutting/secrets
---

# Backend ElevenLabs client

`src-tauri/src/elevenlabs.rs` calls the ElevenLabs HTTP API with `reqwest`.

## Facts (src-tauri/src/elevenlabs.rs)
- `speech_to_speech(api_key, voice_id, input_audio, output_audio)`: posts a multipart form (`audio` as `input.wav`, `model_id` `eleven_multilingual_sts_v2`, `remove_background_noise` `true`) to `/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_128` with header `xi-api-key`, then writes the response bytes to `output_audio`.
- A non-success status returns `ElevenLabs API error {status}: {body}`.
- `test_api_key(api_key)` (command): trims the key, returns false when empty, otherwise GETs `/v1/user` and returns whether the status is success.
- Logs lines prefixed `[elevenlabs]`.

## Called from
src-tauri/src/pipeline.rs (`speech_to_speech`); src/routes/settings/+page.svelte (`test_api_key`).

## Related

- [[building-blocks/backend-pipeline]]
- [[interfaces/external-http-apis]]
- [[crosscutting/secrets]]
