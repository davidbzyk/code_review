---
id: building-blocks/frontend-state
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend state module"
description: "Runes-based AppState class holding config and recording progress, plus the isTauri check."
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
    - crosscutting/state-management
    - runtime/load-config
---

# Frontend state module

`src/lib/state.svelte.ts` exports the single `appState` object that every route reads and writes.

## Exports

- `isTauri(): boolean` checks `window.__TAURI_INTERNALS__`.
- Types `Voice`, `GoogleDrive`, `AppConfig`, `RecordingState` (`ready`, `selecting`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`).
- `appState`, an instance of class `AppState`.

## AppState members

- `config` (`$state<AppConfig>`), `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `recordingDuration`, `ffmpegAvailable` (default `true`).
- `selectedVoice` (`$derived`): first voice with `is_default`, else first voice, else `null`.
- `isConfigured` (`$derived`): API key non-empty and at least one voice.
- `loadConfig()`: tries Tauri `get_config`; then `fetch('/_config.json')`; then `localStorage` key `voiceover-config`.
- `saveConfig()`: writes `localStorage`, then Tauri `save_config` when in Tauri.
- `reset()`: restores the recording fields to their initial values.

It logs through `logger` and calls `invoke` via a local `tauriInvoke` helper.

## Used by

All routes in `src/routes/` and `src/lib/recorder.svelte.ts` (for `isTauri`).

## Related

- [building-blocks/frontend-logger](./frontend-logger.md)
- [runtime/load-config](../runtime/load-config.md)
- [crosscutting/state-management](../crosscutting/state-management.md)
- [crosscutting/configuration](../crosscutting/configuration.md)
- [interfaces/tauri-commands](../interfaces/tauri-commands.md)
