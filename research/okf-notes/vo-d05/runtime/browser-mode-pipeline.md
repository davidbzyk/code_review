---
id: runtime/browser-mode-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Browser mode pipeline
description: Preview-page flow used outside Tauri: ElevenLabs fetch and ffmpeg.wasm splicing.
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
  - resource: src/lib/state.svelte.ts
related:
  - runtime/process-recording-elevenlabs
  - building-blocks/frontend-routes
  - building-blocks/frontend-shell
---

# Browser mode pipeline

`processViaBrowser` runs when `isTauri()` is false.

## Steps

1. It reads the video from `blobStore.getVideo()`; with voice replacement off it calls `downloadBlob` with a `.webm` name.
2. It requires the ElevenLabs key and `selectedVoice`.
3. It takes the audio-only blob from `blobStore.getAudio()`, or runs `extractAudioFromBlob` (decode, resample, `encodeWav`).
4. It posts the audio with `fetch` to `https://api.elevenlabs.io/v1/speech-to-speech/{voice}?output_format=mp3_44100_128`.
5. It loads ffmpeg.wasm from `/ffmpeg/ffmpeg-core.js` and `.wasm`, falling back to `toBlobURL`.
6. It writes `video.webm` and `voice.mp3` and runs ffmpeg with `-c:v copy`, a mute of the first 0.5 s, `libopus` 128k and `-shortest` into `output.webm`.
7. It downloads the output, stores it in `blobStore`, and sets state `saved`.

## Related

- [[runtime/process-recording-elevenlabs]] - Process recording with ElevenLabs
- [[building-blocks/frontend-routes]] - Frontend routes
- [[building-blocks/frontend-shell]] - Frontend shell and utilities
