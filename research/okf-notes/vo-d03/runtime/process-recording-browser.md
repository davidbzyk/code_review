---
id: runtime/process-recording-browser
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Flow: process a recording in the browser"
description: "Steps of processViaBrowser: S2S request and ffmpeg.wasm splice."
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
relations:
  relates_to:
    - building-blocks/page-preview
    - runtime/process-recording-desktop
---

# Flow: process a recording in the browser

This flow runs when `isTauri()` is false; everything happens in the page.

## Steps

1. `processViaBrowser()` reads `window.__voiceover_blob`; it throws when absent.
2. If `voice_replacement_enabled` is off, `downloadBlob` saves the raw `.webm` and the flow ends with `outputPath = 'Downloaded'`.
3. Otherwise it requires an API key and `appState.selectedVoice`.
4. It uses `window.__voiceover_audio_blob`, or calls `extractAudioFromBlob` (decode, resample to 16 kHz mono, `encodeWav`).
5. `fetch` POSTs a `FormData` (`audio`, `model_id`, `remove_background_noise`) to `https://api.elevenlabs.io/v1/speech-to-speech/<voice>`; a non-OK response throws.
6. It imports `@ffmpeg/ffmpeg` and `@ffmpeg/util` and loads the core from `/ffmpeg/ffmpeg-core.js` and `/ffmpeg/ffmpeg-core.wasm`, falling back to `toBlobURL`.
7. It writes `video.webm` and `voice.mp3` into the wasm file system.
8. `exec` copies the video stream, mutes the first 0.5 s of audio, fades in over 0.1 s, encodes `libopus` at 128k with `-shortest` into `output.webm`.
9. It reads the output, terminates the instance, calls `downloadBlob`, and sets `recordingState = 'saved'`.

## Related

- [building-blocks/page-preview](../building-blocks/page-preview.md)
- [runtime/process-recording-desktop](./process-recording-desktop.md)
- [interfaces/external-http-apis](../interfaces/external-http-apis.md)
