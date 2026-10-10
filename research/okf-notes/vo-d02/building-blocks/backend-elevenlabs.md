---
id: building-blocks/backend-elevenlabs
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust ElevenLabs client
description: Speech-to-speech request and API key check against the ElevenLabs API.
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
related:
  - building-blocks/backend-pipeline
  - interfaces/external-http-apis
  - building-blocks/frontend-settings-page
---

src-tauri/src/elevenlabs.rs uses `reqwest` for two calls.

## Functions
- `speech_to_speech(api_key, voice_id, input_audio, output_audio)`: reads the WAV file, posts multipart form fields `audio` (file name `input.wav`, `audio/wav`), `model_id` = `eleven_multilingual_sts_v2`, `remove_background_noise` = `true` to `/v1/speech-to-speech/{voice_id}?output_format=mp3_44100_128` with header `xi-api-key`; writes the response bytes to `output_audio`. A non-success status returns `ElevenLabs API error <status>: <body>`.
- `test_api_key(api_key)` (command): trims the key; empty returns `Ok(false)`; otherwise GET `/v1/user` and returns whether the status is success.

## Called by
`pipeline::process_recording`; src/routes/settings/+page.svelte.

## Related
[[building-blocks/backend-pipeline]], [[interfaces/external-http-apis]]
