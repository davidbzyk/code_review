---
id: building-blocks/frontend-routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend routes"
description: "The SvelteKit pages that make up the user interface."
domain: architecture
tags:
  - building-block
  - frontend
  - svelte
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+layout.svelte
  - resource: src/routes/+layout.ts
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/widget/+layout.ts
related:
  - building-blocks/frontend-state-and-utils
  - building-blocks/frontend-recorder
  - building-blocks/frontend-clients
  - interfaces/tauri-commands
  - runtime/record-screen
  - runtime/process-recording
  - runtime/create-local-voice
---
# Frontend routes

The routes folder holds one Svelte page per screen and a layout that loads config and checks ffmpeg.

## Files and responsibilities

- `+layout.svelte`: on mount calls `appState.loadConfig()`, and in Tauri invokes `check_prerequisites` to set `appState.ffmpegAvailable`; shows an error banner when ffmpeg is missing.
- `+layout.ts` and `widget/+layout.ts`: `ssr = false`, `prerender = true`.
- `+page.svelte` (route `/`): capture mode choice, microphone choice, record, pause, stop, cancel; functions `handleRecord`, `handleStop`, `handlePause`, `handleCancel`; navigates to `/preview` after stop.
- `preview/+page.svelte`: plays the recording and runs `processAndSave`, which calls `processViaTauri` or `processViaBrowser`; `uploadToDrive` sends the result to Drive.
- `settings/+page.svelte`: provider choice, ElevenLabs key test, voice list, local voice list, Google Drive connect and disconnect.
- `create-voice/+page.svelte`: a five-step wizard to build a local voice profile.
- `widget/+page.svelte`: a small recording-status window with pause, stop and cancel buttons.

## Uses

- State and config: [[building-blocks/frontend-state-and-utils]].
- Recording engine and overlays: [[building-blocks/frontend-recorder]].
- Drive and sidecar clients: [[building-blocks/frontend-clients]].
- Rust commands listed in [[interfaces/tauri-commands]].

## Related

- [[runtime/record-screen]]
- [[runtime/process-recording]]
- [[runtime/create-local-voice]]
