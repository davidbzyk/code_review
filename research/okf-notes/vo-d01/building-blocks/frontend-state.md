---
id: building-blocks/frontend-state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend State and Logger"
description: "The shared reactive application state and the console logger."
domain: architecture
tags:
  - building-block
  - svelte
  - state
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/logger.ts
---
# Frontend State and Logger

`state.svelte.ts` exports the singleton `appState`; `logger.ts` exports `logger`.

## Facts
- `AppState` fields use `$state`: `config`, `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `recordingDuration`, `ffmpegAvailable` (src/lib/state.svelte.ts).
- `RecordingState` values: `ready`, `selecting`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`.
- `selectedVoice` and `isConfigured` are `$derived`.
- `loadConfig` tries Tauri `get_config`, then `fetch('/_config.json')`, then `localStorage` key `voiceover-config`.
- `saveConfig` writes `localStorage`, then invokes `save_config` in Tauri. `reset` returns fields to defaults.
- `logger` wraps `console` with prefix `[VO:{category}]` and named helpers such as `pipelineStage` and `driveConnected` (src/lib/logger.ts).

## Used by
Every route and src/lib/recorder.svelte.ts.

## Related
- [[crosscutting/state-management]]
- [[crosscutting/logging]]
- [[interfaces/config-json-shape]]
