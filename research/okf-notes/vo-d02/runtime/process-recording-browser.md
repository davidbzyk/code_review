---
id: runtime/process-recording-browser
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Runtime: process a recording (browser)
description: Flow of processViaBrowser: ElevenLabs by fetch, then ffmpeg.wasm splice and download.
domain: architecture
tags:
  - runtime
  - arc42-6
  - pipeline
  - browser
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: vite.config.ts
  - resource: src/lib/recorder.svelte.ts
related:
  - building-blocks/frontend-preview-page
  - runtime/process-recording-desktop
  - interfaces/external-http-apis
---

In a browser `processViaBrowser()` does the same work without Rust.

1. It reads `window.__voiceover_blob` (set by src/lib/recorder.svelte.ts); throws "No recording data found" when absent.
2. When voice replacement is off, it downloads the raw `.webm` with `downloadBlob` and sets state `saved`.
3. Otherwise it requires the API key and a selected voice.
4. It takes `window.__voiceover_audio_blob`; when missing or empty, `extractAudioFromBlob()` builds a 16 kHz mono WAV, or falls back to sending the WebM.
5. `fetch` POSTs a `FormData` with `audio`, `model_id`, `remove_background_noise` to the ElevenLabs speech-to-speech URL.
6. It imports `@ffmpeg/ffmpeg` and loads core files from `/ffmpeg/ffmpeg-core.js` and `/ffmpeg/ffmpeg-core.wasm`, with a `toBlobURL` fallback.
7. `ffmpegInstance.exec` maps video from input 0 and audio from input 1, copies video, mutes the first 0.5 s of audio with a 0.1 s fade-in, encodes `libopus` at 128k, `-shortest`, to `output.webm`.
8. The result is downloaded as `voiceover-<time>.webm`, stored back in `window.__voiceover_blob`, and state becomes `saved`.

vite.config.ts excludes `@ffmpeg/ffmpeg` and `@ffmpeg/util` from dependency optimisation.

## Related
[[building-blocks/frontend-preview-page]], [[runtime/process-recording-desktop]], [[interfaces/external-http-apis]]
