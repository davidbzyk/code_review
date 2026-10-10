---
id: crosscutting/state-management
schema: okf/schemas/v1/architecture.json
type: Architecture
title: State management
description: Where application state lives: AppState, localStorage, window globals, Tauri events.
domain: architecture
tags:
  - crosscutting
  - arc42-8
  - state
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/+page.svelte
related:
  - building-blocks/frontend-state-and-logging
  - interfaces/tauri-events
  - runtime/config-load-and-save
---

Shared UI state is the `appState` singleton; recorder internals and cross-window signals use other carriers.

## Facts
- `appState` (class `AppState`, `$state` and `$derived` fields) is imported by every route (src/lib/state.svelte.ts).
- `RecordingState` values describe the lifecycle from `ready` to `saved`; `reset()` returns to `ready`.
- Recorder variables (`mediaRecorder`, `screenStream`, chunk arrays) are module-level in src/lib/recorder.svelte.ts.
- Browser-mode blobs travel on `window.__voiceover_blob` and `window.__voiceover_audio_blob`.
- The widget keeps its own `duration` and `isPaused` (src/routes/widget/+page.svelte); the main page keeps `appState.recordingDuration`.
- The widget and main window talk through Tauri events `recording-stop`, `recording-cancel` and `widget-voice-name`.
- Persisted state: `localStorage` and `config.json` ([[runtime/config-load-and-save]]).

## Related
[[building-blocks/frontend-state-and-logging]], [[interfaces/tauri-events]], [[runtime/config-load-and-save]]
