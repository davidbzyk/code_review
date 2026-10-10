---
id: runtime/record-a-session
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Runtime: record a session
description: Step by step flow from the Record button to the /preview route.
domain: architecture
tags:
  - runtime
  - arc42-6
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src/routes/widget/+page.svelte
related:
  - building-blocks/frontend-recorder
  - building-blocks/frontend-record-page
  - building-blocks/backend-recording-commands
  - runtime/process-recording-desktop
---

This flow covers the desktop app from pressing record to arriving at the preview.

1. `handleRecord()` in src/routes/+page.svelte sets state `selecting` and calls `startRecording`.
2. `startRecording` in src/lib/recorder.svelte.ts creates a session id, calls `navigator.mediaDevices.getDisplayMedia` (video only) and `getUserMedia` (audio only).
3. It combines video and audio tracks into one `MediaStream` and starts a `MediaRecorder` with 1000 ms timeslices.
4. Each `ondataavailable` chunk is passed to the command `save_recording_chunk` (src-tauri/src/commands/recording.rs), which writes `chunk_NNNN.webm`.
5. State becomes `recording`; `create_widget_window` opens the widget (src-tauri/src/commands/window.rs); `listen` registers `recording-stop` and `recording-cancel`.
6. The widget (src/routes/widget/+page.svelte) emits `recording-stop` in `handleStop()` and invokes `close_widget_window`.
7. `handleStop()` in src/routes/+page.svelte calls `stopRecording()`.
8. `stopRecording` stops the recorders; in `onstop` it invokes `finalize_recording`, which concatenates the chunks into `<session_id>.webm`.
9. The returned path goes to `appState.recordingPath`; state becomes `recorded`; `goto('/preview')`.

In a browser the chunks stay in memory and `stopRecording` resolves with an object URL (src/lib/recorder.svelte.ts).

## Related
[[building-blocks/frontend-recorder]], [[building-blocks/frontend-record-page]], [[building-blocks/backend-recording-commands]], [[runtime/process-recording-desktop]]
