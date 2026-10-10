---
id: crosscutting/state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Application state"
description: "Where state is held in the frontend and on disk."
domain: architecture
tags:
  - crosscutting
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: crosscutting
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/routes/widget/+page.svelte
related:
  - building-blocks/frontend-state
  - building-blocks/frontend-recorder
---

# Application state

UI state is the `appState` singleton; recorder state is module-level variables.

## Facts
- `appState` holds `recordingState`, paths, progress and config (src/lib/state.svelte.ts).
- `recorder.svelte.ts` keeps `mediaRecorder`, `audioRecorder`, `screenStream`, `audioStream`, `chunkIndex`, `sessionId`, `recordedChunks`, `audioChunks` as module variables.
- Browser mode passes blobs between routes on `window.__voiceover_blob` and `window.__voiceover_audio_blob` (src/lib/recorder.svelte.ts).
- The widget page keeps its own `duration`, `isPaused`, `voiceName` (src/routes/widget/+page.svelte).
- On disk: temp chunks under `voiceover-recordings`, `config.json` in app data.

## Related

- [[building-blocks/frontend-state]]
- [[building-blocks/frontend-recorder]]
