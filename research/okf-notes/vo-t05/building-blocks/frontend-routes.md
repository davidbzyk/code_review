---
id: building-blocks/frontend-routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Frontend Routes
description: The five SvelteKit pages and the shared layout that make up the user interface.
domain: architecture
tags:
  - building-block
  - frontend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+layout.svelte
  - resource: src/routes/+layout.ts
  - resource: src/routes/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/create-voice/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/widget/+layout.ts
  - resource: src/app.html
  - resource: src/app.css
  - resource: src/app.d.ts
related:
  - building-blocks/frontend-recorder
  - building-blocks/frontend-state-and-config
  - building-blocks/frontend-integrations
  - runtime/record-screen
  - runtime/create-voice-profile
---

# Frontend Routes

The routes own the screens: record, settings, voice-profile wizard, preview and save, and a small recording widget.

## Pages

- `/` (src/routes/+page.svelte): capture mode, audio device and voice choice; `handleRecord`, `handleStop`, `handlePause`, `handleCancel`; navigates to `/preview` with `goto`.
- `/preview` (src/routes/preview/+page.svelte): `processAndSave` runs `processViaTauri` or `processViaBrowser`; `uploadToDrive`; `discard`, `newRecording`.
- `/settings` (src/routes/settings/+page.svelte): provider toggle, `testApiKey`, voices list, `connectDrive`, `disconnectDrive`, local voice list and delete.
- `/create-voice` (src/routes/create-voice/+page.svelte): a stepped wizard (`step` variable) using `VoiceboxClient`.
- `/widget` (src/routes/widget/+page.svelte): timer plus pause, stop and cancel buttons that emit events.

## Layout

- `+layout.svelte` calls `appState.loadConfig()` in `onMount`, invokes `check_prerequisites` under Tauri, and shows a banner when `appState.ffmpegAvailable` is false.
- `+layout.ts` and `widget/+layout.ts` set `ssr = false` and `prerender = true`.
- `src/app.html` is the page shell; `src/app.css` holds shared styles; `src/app.d.ts` declares the `App` namespace.

## Uses

State in `$lib/state.svelte`, recorder in `$lib/recorder.svelte`, `$lib/drive`, `$lib/voicebox`, `$lib/tauri`, `$lib/logger`, `$lib/blobStore`.

## Related

- [Frontend Recorder](./frontend-recorder.md)
- [Frontend State and Config](./frontend-state-and-config.md)
- [Frontend Integrations](./frontend-integrations.md)
- [Flow: Record the Screen](../runtime/record-screen.md)
- [Flow: Create a Local Voice Profile](../runtime/create-voice-profile.md)
