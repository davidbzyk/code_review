---
id: runtime/process-recording-browser
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process recording in a browser"
description: "In browser mode the preview page calls ElevenLabs with fetch and splices audio with ffmpeg.wasm, then downloads a WebM."
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
  - resource: static/robots.txt
  - resource: vite.config.ts
relations:
  relates_to:
    - building-blocks/frontend-pages
    - interfaces/external-http-apis
    - runtime/process-recording-tauri
---
# Process recording in a browser

`processViaBrowser()` runs the whole pipeline inside the page (src/routes/preview/+page.svelte).

## Steps

1. Read `window.__voiceover_blob`; throw `No recording data found` if absent.
2. With voice replacement off, call `downloadBlob(blob, 'voiceover-<time>.webm')`, set `outputPath` to `Downloaded` and state `saved`.
3. Otherwise require an API key and a selected voice.
4. Use `window.__voiceover_audio_blob`; if empty, call `extractAudioFromBlob`, which decodes audio, rejects more than 300 seconds, resamples to 16 kHz mono with `OfflineAudioContext`, and encodes WAV with `encodeWav`. A decode failure falls back to the raw WebM.
5. POST a `FormData` (`audio`, `model_id`, `remove_background_noise`) to `https://api.elevenlabs.io/v1/speech-to-speech/<voice>?output_format=mp3_44100_128` with header `xi-api-key`.
6. Import `@ffmpeg/ffmpeg` and `@ffmpeg/util`, then `load` the core from `/ffmpeg/ffmpeg-core.js` and `.wasm`; on failure retry through `toBlobURL`.
7. Write `video.webm` and `voice.mp3`, then `exec` ffmpeg with `-c:v copy`, an audio filter that mutes the first 0.5 s and fades in, and `-c:a libopus`, producing `output.webm`.
8. `readFile`, terminate ffmpeg, call `downloadBlob`, set `outputPath` and state `saved`.

## Related

[[building-blocks/frontend-pages]], [[interfaces/external-http-apis]], [[runtime/process-recording-tauri]]
