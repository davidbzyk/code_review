---
id: building-blocks/frontend-routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend Routes
description: SvelteKit route files that make up the pages of the webview.
domain: architecture
tags:
  - building-block
  - frontend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+layout.ts
  - resource: src/routes/+layout.svelte
  - resource: src/routes/(app)/+layout.svelte
  - resource: src/routes/(app)/+layout.ts
  - resource: src/routes/(app)/+page.svelte
  - resource: src/routes/(app)/library/+page.svelte
  - resource: src/routes/(app)/preview/+page.svelte
  - resource: src/routes/(app)/settings/+page.svelte
  - resource: src/routes/(app)/create-voice/+page.svelte
  - resource: src/routes/widget/+layout.ts
  - resource: src/routes/widget/+page.svelte
relations:
  relates_to:
    - building-blocks/frontend-state-and-ipc
    - building-blocks/frontend-recorder
    - building-blocks/frontend-components
    - runtime/record-and-process-recording
---
# Frontend Routes

The routes folder holds one page per user task and two layouts that load config and frame the pages.

## Files and responsibility

- `+layout.svelte` runs `appState.loadConfig()` on mount, calls `check_prerequisites`, and shows a banner when ffmpeg is missing.
- `(app)/+layout.svelte` renders `Sidebar` and `StatusBar` around the pages.
- `(app)/+page.svelte` (route `/`): capture mode choice, `handleRecord`, `handlePause`, `handleStop`, `handleCancel`; on stop it sets state `recorded` and goes to `/preview`.
- `(app)/preview/+page.svelte`: `processAndSave` picks `processViaTauri` or `processViaBrowser`; `uploadToDrive`; `discard`; `newRecording`.
- `(app)/library/+page.svelte`: loads `libraryState` and lists `RecordingCard` items.
- `(app)/settings/+page.svelte`: tabs `voice`, `recording`, `cloud`; `testApiKey`, `connectDrive`, `disconnectDrive`, `setProvider`, `setLocalVoice`.
- `(app)/create-voice/+page.svelte`: voice profile wizard, using `VoiceboxClient`.
- `widget/+page.svelte`: small recording widget with a timer; `handlePause`, `handleStop`, `handleCancel` emit events.
- The three `+layout.ts` files set `ssr = false` and `prerender = true`.

## Uses

State in `src/lib/state.svelte.ts`, recorder functions in `src/lib/recorder.svelte.ts`, Tauri commands through `src/lib/tauri.ts`.

## Related

- [Frontend State and IPC](frontend-state-and-ipc.md)
- [Frontend Recorder](frontend-recorder.md)
- [Frontend Components and Styles](frontend-components.md)
- [Flow: Record and Process a Recording](../runtime/record-and-process-recording.md)
