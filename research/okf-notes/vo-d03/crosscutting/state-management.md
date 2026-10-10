---
id: crosscutting/state-management
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "State management"
description: "Shared runes state in AppState plus module-level state in the recorder and Rust temp files."
domain: architecture
tags:
  - crosscutting
  - state
  - arc42-8
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
  - resource: src/routes/preview/+page.svelte
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/frontend-recorder
---

# State management

Application state is one `appState` object; recorder objects and temp files hold the media.

## Facts

- `appState` (`src/lib/state.svelte.ts`) holds `config`, `recordingState`, `recordingPath`, `outputPath`, progress fields, `errorMessage`, `ffmpegAvailable`; `reset()` clears the recording fields.
- Module-level variables in `src/lib/recorder.svelte.ts`: `mediaRecorder`, `audioRecorder`, `screenStream`, `audioStream`, `chunkIndex`, `sessionId`, `recordedChunks`, `audioChunks`.
- Browser mode passes blobs between routes on `window.__voiceover_blob` and `window.__voiceover_audio_blob` (`src/lib/recorder.svelte.ts`, `src/routes/preview/+page.svelte`).
- Desktop mode passes a file path in `appState.recordingPath`; chunks live under the temp directory `voiceover-recordings` (`src-tauri/src/commands/recording.rs`).
- The widget window keeps its own `duration`, `isPaused` and `voiceName` (`src/routes/widget/+page.svelte`).
- Route-local `$state` variables hold form and progress values in each page.

## Related

- [building-blocks/frontend-state](../building-blocks/frontend-state.md)
- [building-blocks/frontend-recorder](../building-blocks/frontend-recorder.md)
- [crosscutting/configuration](./configuration.md)
