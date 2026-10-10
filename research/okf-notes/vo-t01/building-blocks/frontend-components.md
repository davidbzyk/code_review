---
id: building-blocks/frontend-components
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend Components and Styles
description: Shared Svelte components, global CSS and the HTML shell.
domain: architecture
tags:
  - building-block
  - frontend
  - ui
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/RecordingCard.svelte
  - resource: src/lib/Sidebar.svelte
  - resource: src/lib/StatusBar.svelte
  - resource: src/app.css
  - resource: src/app.html
relations:
  relates_to:
    - building-blocks/frontend-routes
    - building-blocks/frontend-state-and-ipc
    - runtime/upload-recording-to-drive
---
# Frontend Components and Styles

These files draw the sidebar, status bar, library cards and global styling.

## Files

- `Sidebar.svelte`: `navItems` for `/`, `/library`, `/settings`; `isActive` also marks `/preview` under Record and `/create-voice` under Settings; navigates with `goto`.
- `StatusBar.svelte`: `checkSidecar` calls `get_sidecar_status`; `resolveLocalVoiceName` calls `list_local_voices`.
- `RecordingCard.svelte`: `loadThumbnail` calls `generate_thumbnail` then `read_file_bytes`; `handleDelete`, `handleOpen`, `handleReveal`, `startRename`, `commitRename`, `handleUploadToDrive`.
- `app.css`: global body colours and shared page styles for the settings and create-voice routes.
- `app.html`: the SvelteKit page shell with a fixed dark body background.

## Uses

`libraryState` from `src/lib/library.svelte.ts`, `refreshDriveToken` from `src/lib/drive.ts`, `appState`.

## Related

- [Frontend Routes](frontend-routes.md)
- [Frontend State and IPC](frontend-state-and-ipc.md)
- [Flow: Connect and Upload to Google Drive](../runtime/upload-recording-to-drive.md)
