---
id: building-blocks/elevenlabs-client
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "ElevenLabs Client"
description: "Backend module that calls the ElevenLabs speech-to-speech and user endpoints."
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
---
# ElevenLabs Client

`elevenlabs.rs` sends audio for voice conversion and validates an API key.

## Facts
- `speech_to_speech(api_key, voice_id, input_audio, output_audio)` posts a multipart form with `audio` (`input.wav`, `audio/wav`), `model_id` `eleven_multilingual_sts_v2` and `remove_background_noise` `true` to `/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_128`, header `xi-api-key`.
- A non-success status returns `Err("ElevenLabs API error {status}: {body}")`; success bytes are written to `output_audio`.
- `test_api_key(api_key)` is a command: trims the key, returns `Ok(false)` if empty, otherwise GETs `/v1/user` and returns whether the status is success.
- Both log through the `log` crate with the prefix `[elevenlabs]`.

## Called by
`pipeline::process_recording`; `testApiKey` in src/routes/settings/+page.svelte.

## Related
- [[interfaces/external-http-apis]]
- [[building-blocks/media-pipeline]]
- [[crosscutting/secrets-handling]]
