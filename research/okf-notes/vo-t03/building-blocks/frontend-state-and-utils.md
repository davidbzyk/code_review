---
id: building-blocks/frontend-state-and-utils
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend state and utilities"
description: "Shared reactive state, the Tauri invoke wrapper, the logger, the blob store and the HTML and CSS shell."
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
  - resource: src/lib/tauri.ts
  - resource: src/lib/logger.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/index.ts
  - resource: src/app.d.ts
  - resource: src/app.css
  - resource: src/app.html
related:
  - crosscutting/configuration
  - crosscutting/logging
  - crosscutting/state-management
  - building-blocks/frontend-routes
---
# Frontend state and utilities

These files hold the state and helpers every page imports.

## Files

- `state.svelte.ts`: class `AppState` exported as `appState`; holds `config`, `recordingState`, `recordingPath`, `outputPath`, processing progress, `webcamStream`, `webcamVideoEl`, `ffmpegAvailable`; derived `selectedVoice` and `isConfigured`; methods `loadConfig`, `saveConfig`, `reset`. Also exports `isTauri()` and the types `Voice`, `GoogleDrive`, `AppConfig`, `RecordingState`.
- `tauri.ts`: `tauriInvoke<T>(cmd, args)` imports `@tauri-apps/api/core` lazily and calls `invoke`.
- `logger.ts`: `logger` object with named helpers and generic `info`, `warn`, `error`, `debug`; every line is prefixed `[VO:<category>]`.
- `blobStore.ts`: module-private `videoBlob` and `audioBlob` with `setVideo`, `getVideo`, `setAudio`, `getAudio`, `clear`.
- `index.ts`: a comment only.
- `app.d.ts`: empty `App` namespace declarations.
- `app.css`: dark background `#0f172a` and base font.
- `app.html`: the SvelteKit page template.

## Used by

All routes and the recorder import `appState` and `logger`. `blobStore` is used by the recorder and the preview page in browser mode.

## Related

- [[crosscutting/configuration]]
- [[crosscutting/logging]]
- [[crosscutting/state-management]]
- [[building-blocks/frontend-routes]]
