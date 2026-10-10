---
id: runtime/browser-mode-processing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Browser-Mode Processing
description: How /preview processes a recording when the app runs without Tauri.
domain: architecture
tags:
  - runtime
  - frontend
  - elevenlabs
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/blobStore.ts
  - resource: src/lib/state.svelte.ts
related:
  - building-blocks/frontend-routes
  - building-blocks/frontend-state-and-config
  - runtime/process-recording-elevenlabs
---

# Flow: Browser-Mode Processing

Trigger: `processAndSave` calls `processViaBrowser` when `isTauri()` is false (src/routes/preview/+page.svelte).

1. It reads `blobStore.getVideo()`; with voice replacement off it calls `downloadBlob` and sets state `saved`.
2. Otherwise it needs `elevenlabs_api_key` and `appState.selectedVoice`.
3. It uses `blobStore.getAudio()`, or `extractAudioFromBlob` and `encodeWav` when no audio blob exists.
4. It posts the audio as form data to `https://api.elevenlabs.io/v1/speech-to-speech/{voice.id}?output_format=mp3_44100_128`.
5. It imports `@ffmpeg/ffmpeg`, loads `/ffmpeg/ffmpeg-core.js` and `.wasm` (falling back to `toBlobURL`), and runs one `exec` that mutes the first 0.5 s and encodes with `libopus`.
6. It reads `output.webm`, calls `downloadBlob`, stores it with `blobStore.setVideo`, and sets `outputPath` to `Downloaded: <filename>`.

## Related

- [Frontend Routes](../building-blocks/frontend-routes.md)
- [Frontend State and Config](../building-blocks/frontend-state-and-config.md)
- [Flow: Process a Recording (ElevenLabs)](./process-recording-elevenlabs.md)
