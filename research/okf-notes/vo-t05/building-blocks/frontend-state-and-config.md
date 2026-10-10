---
id: building-blocks/frontend-state-and-config
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend State and Config
description: The shared reactive app state, config persistence, logger, blob store and the Tauri invoke wrapper.
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
  - resource: src/lib/blobStore.ts
  - resource: src/lib/logger.ts
  - resource: src/lib/tauri.ts
  - resource: src/lib/index.ts
related:
  - crosscutting/state-management
  - crosscutting/logging
  - runtime/config-load-save
  - building-blocks/rust-config-and-secrets
---

# Frontend State and Config

`appState`, an instance of class `AppState`, holds all cross-page state as Svelte `$state` fields.

## Facts

- `AppConfig`, `Voice`, `GoogleDrive` and `RecordingState` types are exported (src/lib/state.svelte.ts). `RecordingState` has nine values from `ready` to `saved`.
- `loadConfig()` and `saveConfig()` read and write Tauri app data, `static/_config.json` and `localStorage` under key `voiceover-config` (src/lib/state.svelte.ts).
- `sanitizeForStorage` blanks the API key, client secret and tokens before writing to `localStorage`.
- `selectedVoice` and `isConfigured` are `$derived` values; `reset()` stops webcam tracks and clears session fields.
- `isTauri()` tests `window.__TAURI_INTERNALS__`.
- `blobStore` keeps one video blob and one audio blob in module variables (src/lib/blobStore.ts).
- `tauriInvoke<T>(cmd, args)` dynamically imports `@tauri-apps/api/core` and calls `invoke` (src/lib/tauri.ts).
- `logger` prints prefixed console lines `[VO:category]` (src/lib/logger.ts).
- src/lib/index.ts holds only a comment.

## Used by

Every route and `$lib` module imports `appState`.

## Related

- [State Management](../crosscutting/state-management.md)
- [Logging](../crosscutting/logging.md)
- [Flow: Load and Save Config](../runtime/config-load-save.md)
- [Rust Config and Secrets](./rust-config-and-secrets.md)
