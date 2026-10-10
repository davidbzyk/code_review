---
id: runtime/process-recording-browser-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Process recording in browser mode"
description: "processViaBrowser: S2S fetch and ffmpeg.wasm splice."
domain: architecture
tags:
  - runtime
  - pipeline
  - browser
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src/routes/preview/+page.svelte
related:
  - building-blocks/route-preview
  - interfaces/external-http-apis
  - runtime/process-recording-desktop-flow
---

# Process recording in browser mode

Outside Tauri, `processViaBrowser()` does the whole job in the page and downloads a WebM.

## Steps (src/routes/preview/+page.svelte)
1. Reads `window.__voiceover_blob`; throws "No recording data found" if absent.
2. With voice replacement off: `downloadBlob(blob, voiceover-<time>.webm)` and state `saved`.
3. Otherwise requires the API key and a selected voice.
4. Uses `window.__voiceover_audio_blob`; if missing or empty, `extractAudioFromBlob()` decodes audio, rejects clips over 300 s, resamples to 16 kHz mono with `OfflineAudioContext`, encodes with `encodeWav()`.
5. `fetch` posts `audio`, `model_id`, `remove_background_noise` to the ElevenLabs speech-to-speech URL.
6. Imports `@ffmpeg/ffmpeg`, loads `/ffmpeg/ffmpeg-core.js` and `/ffmpeg/ffmpeg-core.wasm` (fallback `toBlobURL`).
7. Writes `video.webm` and `voice.mp3`, runs `exec` with `-c:v copy`, a volume filter muting 0 to 0.5 s, `libopus` at 128k, `-shortest`.
8. Reads `output.webm`, calls `downloadBlob`, stores the blob on `window.__voiceover_blob`, sets state `saved`.

## Related

- [[building-blocks/route-preview]]
- [[interfaces/external-http-apis]]
- [[runtime/process-recording-desktop-flow]]
