---
id: building-blocks/frontend-pages
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend pages"
description: "Four Svelte routes drive the user flow: record, preview and process, settings, and the floating recording widget."
domain: architecture
tags:
  - building-block
  - frontend
  - ui
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/widget/+page.svelte
relations:
  relates_to:
    - building-blocks/frontend-state
    - building-blocks/frontend-recorder
    - runtime/process-recording-tauri
    - runtime/process-recording-browser
    - runtime/drive-upload-flow
    - runtime/widget-window-flow
---
# Frontend pages

Each route is one Svelte component with its own script, markup and styles.

## Routes

- `/` (src/routes/+page.svelte): capture mode cards (`fullscreen`, `window`, `region`), microphone choice, webcam and voice toggles. Functions `handleRecord`, `handleStop`, `handleCancel`, `handlePause`, `formatTime`. After stop it calls `goto('/preview')`; a Settings button calls `goto('/settings')`.
- `/preview` (src/routes/preview/+page.svelte): shows the recording, then `processAndSave` runs `processViaTauri` or `processViaBrowser`. Also `extractAudioFromBlob`, `encodeWav`, `downloadBlob`, `refreshDriveToken`, `driveUploadWithToken`, `uploadToDrive`, `discard`, `newRecording`.
- `/settings` (src/routes/settings/+page.svelte): `saveAndBack`, `testApiKey`, `addVoice`, `removeVoice`, `setDefault`, `connectDrive`, `disconnectDrive`.
- `/widget` (src/routes/widget/+page.svelte): a timer with pause, stop and cancel; `handlePause`, `handleStop`, `handleCancel` emit events and call `close_widget_window`.

## Uses

`appState`, `isTauri` (src/lib/state.svelte.ts); the recorder functions (src/lib/recorder.svelte.ts); `logger`; Tauri `invoke`, `Channel`, `emit`, `listen`.

## Related

[[building-blocks/frontend-state]], [[building-blocks/frontend-recorder]], [[runtime/process-recording-tauri]], [[runtime/process-recording-browser]]
