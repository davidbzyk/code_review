---
id: building-blocks/frontend-state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend shared state"
description: "The AppState class, config types and the isTauri helper."
domain: architecture
tags:
  - frontend
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/lib/state.svelte.ts
related:
  - runtime/config-load-save-flow
  - crosscutting/state
  - crosscutting/configuration
  - building-blocks/frontend-logger
---

# Frontend shared state

`src/lib/state.svelte.ts` holds the single runes-based state object `appState` and the types the pages share.

## Public items (src/lib/state.svelte.ts)
- `isTauri()`: true when `window.__TAURI_INTERNALS__` exists.
- Types `Voice`, `GoogleDrive`, `AppConfig`, `RecordingState` (`ready`, `selecting`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`).
- `class AppState` with `$state` fields: `config`, `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `recordingDuration`, `ffmpegAvailable`.
- `$derived` fields: `selectedVoice` (default voice, else first, else null) and `isConfigured`.
- Methods `loadConfig()`, `saveConfig()`, `reset()`.
- Export `appState = new AppState()`.

## Uses
`logger` (src/lib/logger.ts); Tauri commands `get_config` and `save_config`; `fetch('/_config.json')`; `localStorage` key `voiceover-config`.

## Used by
Every route and `src/lib/recorder.svelte.ts`.

## Related

- [[runtime/config-load-save-flow]]
- [[crosscutting/state]]
- [[crosscutting/configuration]]
- [[building-blocks/frontend-logger]]
