---
id: runtime/process-recording-browser
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process Recording in the Browser"
description: "The in-page path that calls ElevenLabs with fetch and splices with ffmpeg.wasm."
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
---
# Process Recording in the Browser

`processViaBrowser` works from blobs stored on `window`.

## Steps
1. Read `window.__voiceover_blob`; throw if absent.
2. If voice replacement is off, `downloadBlob` the raw WebM and set `saved`.
3. Otherwise require the API key and `selectedVoice`.
4. Take `window.__voiceover_audio_blob`, or call `extractAudioFromBlob` (decodes, rejects over 300 s, resamples to 16 kHz mono, `encodeWav`).
5. POST a `FormData` (`audio`, `model_id`, `remove_background_noise`) to the ElevenLabs speech-to-speech URL.
6. Load `FFmpeg` with core files from `/ffmpeg/ffmpeg-core.js` and `.wasm`, falling back to `toBlobURL`.
7. `exec` ffmpeg with `-c:v copy`, a volume filter muting the first 0.5 s, and `libopus` at 128k into `output.webm`.
8. `downloadBlob` the result, keep it in `__voiceover_blob`, set `saved`.

## Related
- [[building-blocks/preview-screen]]
- [[runtime/process-recording-desktop]]
- [[crosscutting/dual-runtime-mode]]
