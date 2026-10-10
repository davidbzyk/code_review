---
id: crosscutting/state-management
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "State Management"
description: "Reactive state with Svelte runes and the recording state machine."
domain: architecture
tags:
  - crosscutting
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
---
# State Management

One `AppState` instance holds UI and config state for all routes.

## Facts
- `appState` is a class instance with `$state` fields and `$derived` getters (src/lib/state.svelte.ts).
- `recordingState` moves `ready`, `selecting`, `recording`, `paused`, `recorded`, then `saved` after processing (src/routes/+page.svelte, src/routes/preview/+page.svelte).
- `reset()` returns the recording fields to defaults; `discard` and `newRecording` call it.
- Blobs travel between routes on `window.__voiceover_blob` and `window.__voiceover_audio_blob` (src/lib/recorder.svelte.ts).
- Per-route UI flags use local `$state`, such as `isProcessing` and `isUploading`.

## Related
- [[building-blocks/frontend-state]]
- [[crosscutting/dual-runtime-mode]]
- [[runtime/record-screen-and-voice]]
