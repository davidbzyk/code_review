---
id: building-blocks/frontend-state-and-ipc
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend State and IPC
description: Shared reactive state, the Tauri invoke wrapper and the in-memory blob store.
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
  - resource: src/lib/library.svelte.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/tauri.ts
  - resource: src/lib/index.ts
  - resource: src/app.d.ts
relations:
  relates_to:
    - crosscutting/configuration
    - crosscutting/state-management
    - building-blocks/frontend-routes
    - interfaces/tauri-commands-app
---
# Frontend State and IPC

These modules hold the app state and give the webview one way to call Rust.

## Files

- `state.svelte.ts` exports `appState`, an `AppState` class with `$state` fields (`config`, `recordingState`, `recordingPath`, `outputPath`, `processingProgress`, `errorMessage`, `libraryStale`), the derived `selectedVoice` and `isConfigured`, and the methods `loadConfig`, `saveConfig`, `reset`. It also exports `isTauri()` and the types `AppConfig`, `Voice`, `GoogleDrive`, `RecordingState`.
- `library.svelte.ts` exports `libraryState` (`LibraryState`): `load`, `deleteRecording`, `openInSystem`, `revealInFinder`, `renameRecording`, `updateRecordingMeta`, `setSortBy`, and derived `sorted` and `totalSize`.
- `blobStore.ts` exports `blobStore` with `setVideo`, `getVideo`, `setAudio`, `getAudio`, `clear`; the blobs sit in module variables.
- `tauri.ts` exports `tauriInvoke(cmd, args)`, which imports `@tauri-apps/api/core` and calls `invoke`.
- `index.ts` holds only a comment about the `$lib` alias.
- `app.d.ts` declares an empty `App` namespace.

## Calls

`loadConfig` and `saveConfig` call `get_config` and `save_config`; `libraryState` calls `list_recordings`, `delete_recording`, `open_in_system`, `reveal_in_finder`, `rename_recording`.

## Related

- [Configuration](../crosscutting/configuration.md)
- [State Management](../crosscutting/state-management.md)
- [Frontend Routes](frontend-routes.md)
- [Tauri Commands: Config, Recording, Library, Drive, Window](../interfaces/tauri-commands-app.md)
