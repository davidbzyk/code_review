---
id: runtime/process-recording-browser
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process Recording in the Browser"
description: "The browser-mode path that calls ElevenLabs directly and splices audio with ffmpeg.wasm."
domain: architecture
tags:
  - runtime
  - pipeline
  - browser
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/blobStore.ts
related:
  - runtime/process-recording-desktop
  - building-blocks/frontend-routes
---
# Process Recording in the Browser

`processViaBrowser` does the whole job inside the page.

## Steps
1. Read the video with `blobStore.getVideo()`; if missing it throws "No recording data found".
2. If `voice_replacement_enabled` is false it calls `downloadBlob` with a `.webm` name and sets `outputPath` to `Downloaded`.
3. Otherwise it needs `elevenlabs_api_key` and `selectedVoice`.
4. It uses `blobStore.getAudio()`, or `extractAudioFromBlob` (decode, resample, `encodeWav`) when empty.
5. It posts form data to `https://api.elevenlabs.io/v1/speech-to-speech/<voice id>?output_format=mp3_44100_128`.
6. It loads `FFmpeg` from `@ffmpeg/ffmpeg` with core files at `/ffmpeg/ffmpeg-core.js` and `/ffmpeg/ffmpeg-core.wasm`, with a `toBlobURL` fallback.
7. It writes `video.webm` and `voice.mp3`, runs `exec`, reads `output.webm`, and stores it with `blobStore.setVideo`.

## Related
- [Process Recording on Desktop](./process-recording-desktop.md)
- [Frontend Routes](../building-blocks/frontend-routes.md)
