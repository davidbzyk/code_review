---
id: building-blocks/frontend-state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend state module"
description: "state.svelte.ts defines the AppConfig types, the AppState class and the isTauri check that every page uses."
domain: architecture
tags:
  - building-block
  - frontend
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
relations:
  relates_to:
    - building-blocks/frontend-pages
    - crosscutting/state-management
    - crosscutting/configuration
    - runtime/config-load-and-save
---
# Frontend state module

The state module owns the reactive application state and config persistence for the frontend (src/lib/state.svelte.ts).

## Public surface

- `isTauri()`: true when `window.__TAURI_INTERNALS__` exists.
- Types `Voice`, `GoogleDrive`, `AppConfig`, `RecordingState` (`ready`, `selecting`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`).
- Class `AppState`, exported as the singleton `appState`.
  - Rune fields: `config`, `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `recordingDuration`, `ffmpegAvailable`.
  - Derived: `selectedVoice` (default voice, else first voice, else null) and `isConfigured` (API key set and at least one voice).
  - Methods: `loadConfig()`, `saveConfig()`, `reset()`.

## Uses

- `logger` from src/lib/logger.ts.
- Tauri commands `get_config` and `save_config` through a dynamic import of `@tauri-apps/api/core`.
- `fetch('/_config.json')` and `localStorage` under the key `voiceover-config`.

## Related

[[building-blocks/frontend-pages]], [[crosscutting/state-management]], [[crosscutting/configuration]], [[runtime/config-load-and-save]]
