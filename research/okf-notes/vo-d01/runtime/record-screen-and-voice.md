---
id: runtime/record-screen-and-voice
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Record Screen and Voice"
description: "Flow from pressing Record to the /preview route."
domain: architecture
tags:
  - runtime
  - recording
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
---
# Record Screen and Voice

A recording runs from the home route through `MediaRecorder` into temp files.

## Steps
1. `handleRecord` in src/routes/+page.svelte sets `selecting` and calls `startRecording`.
2. `startRecording` (src/lib/recorder.svelte.ts) obtains screen and microphone streams and starts `MediaRecorder` with a 1000 ms timeslice.
3. Each `ondataavailable` chunk is sent to `save_recording_chunk` (`save_recording_chunk` in src-tauri/src/commands/recording.rs) in Tauri, or kept in memory in a browser.
4. `handleRecord` invokes `create_widget_window` (src-tauri/src/commands/window.rs) in Tauri.
5. `handleStop` calls `stopRecording`; in Tauri `finalize_recording` joins chunks into `{session_id}.webm`.
6. `handleStop` stores `recordingPath` and calls `goto('/preview')`.

## Related
- [[building-blocks/frontend-recorder]]
- [[building-blocks/recording-commands]]
- [[runtime/process-recording-desktop]]
