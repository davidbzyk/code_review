---
id: building-blocks/frontend-state-and-logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend state and logging
description: The shared AppState class, config types, Tauri detection and the console logger.
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
  - resource: src/lib/logger.ts
related:
  - crosscutting/state-management
  - crosscutting/logging
  - runtime/config-load-and-save
  - interfaces/config-data-shape
---

src/lib/state.svelte.ts holds one runes-based `AppState` instance named `appState`; src/lib/logger.ts holds the `logger` object.

## state.svelte.ts
- `isTauri()`: true when `window.__TAURI_INTERNALS__` exists.
- Types: `Voice`, `GoogleDrive`, `AppConfig`, `RecordingState` (`ready`, `selecting`, `recording`, `paused`, `recorded`, `processing`, `complete`, `saved`).
- `AppState` fields (`$state`): `config`, `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `processingStage`, `errorMessage`, `recordingDuration`, `ffmpegAvailable`.
- Derived: `selectedVoice` (default voice, else first, else null) and `isConfigured` (API key set and at least one voice).
- Methods: `loadConfig()`, `saveConfig()`, `reset()`.
- Local helper `tauriInvoke` dynamically imports `@tauri-apps/api/core`.

## logger.ts
`log(level, category, message, data)` writes to `console` with a `[VO:<category>]` prefix, a colour per level and an ISO time slice. The `logger` object has typed helpers for config, recording, ElevenLabs, pipeline and drive events plus `info`, `warn`, `error`, `debug`.

## Used by
src/lib/recorder.svelte.ts, src/routes/+layout.svelte, src/routes/+page.svelte, src/routes/preview/+page.svelte, src/routes/settings/+page.svelte, src/routes/widget/+page.svelte.

## Related
[[crosscutting/state-management]], [[crosscutting/logging]], [[runtime/config-load-and-save]], [[interfaces/config-data-shape]]
