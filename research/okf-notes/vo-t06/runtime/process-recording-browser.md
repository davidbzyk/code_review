---
id: runtime/process-recording-browser
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process Recording, Browser"
description: "The browser path that calls ElevenLabs directly and splices audio with ffmpeg.wasm."
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
relations:
  relates_to:
    - building-blocks/route-preview
    - interfaces/external-http-apis
---

Without Tauri, `processViaBrowser()` in `src/routes/preview/+page.svelte` does the work in the page.

## Steps

1. Read the video with `blobStore.getVideo()`; throw "No recording data found" when empty.
2. Voice replacement off: `downloadBlob` saves `voiceover-<time>.webm` and the state becomes `saved`.
3. Voice replacement on: require `elevenlabs_api_key` and a selected voice.
4. Take `blobStore.getAudio()`; when empty, `extractAudioFromBlob` builds a 16 kHz mono WAV with `encodeWav`.
5. `fetch` posts a `FormData` (`audio`, `model_id`, `remove_background_noise`) to `https://api.elevenlabs.io/v1/speech-to-speech/<voice id>?output_format=mp3_44100_128` with header `xi-api-key`.
6. Load `@ffmpeg/ffmpeg` with core files from `/ffmpeg/ffmpeg-core.js` and `/ffmpeg/ffmpeg-core.wasm`; on failure retry through `toBlobURL`.
7. `writeFile` stores `video.webm` and `voice.mp3`; `exec` copies video, mutes the first 0.5 s of audio, fades in over 0.1 s, encodes `libopus` at 128k with `-shortest` to `output.webm`.
8. `readFile` returns the result; `downloadBlob` saves it and `blobStore.setVideo` replaces the video.
9. State becomes `saved` with `outputPath` "Downloaded: <name>".

## Related

- [Preview route](../building-blocks/route-preview.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
