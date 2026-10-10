---
id: runtime/record-and-process-recording
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Record and Process a Recording
description: From the Record button to the saved MP4.
domain: architecture
tags:
  - runtime
  - flow
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/(app)/+page.svelte
  - resource: src/lib/recorder.svelte.ts
  - resource: src-tauri/src/commands/recording.rs
  - resource: src/routes/(app)/preview/+page.svelte
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/src/library.rs
relations:
  relates_to:
    - building-blocks/frontend-recorder
    - building-blocks/rust-pipeline
    - runtime/local-voice-conversion
    - interfaces/events-and-channels
---
# Flow: Record and Process a Recording

This flow runs when a user records the screen and saves the result in the desktop app.

1. `handleRecord` in `src/routes/(app)/+page.svelte` calls `startRecording` in `src/lib/recorder.svelte.ts`.
2. `startRecording` calls `getDisplayMedia` and starts a `MediaRecorder` with a 5000 ms timeslice.
3. Each data event calls `save_recording_chunk` (`src-tauri/src/commands/recording.rs`).
4. `handleStop` calls `stopRecording`, which calls `finalize_recording` and returns the WebM path; state becomes `recorded` and the page goes to `/preview`.
5. `processAndSave` in `src/routes/(app)/preview/+page.svelte` runs `processViaTauri`, which calls `process_recording` with a `Channel`.
6. `process_recording` (`src-tauri/src/pipeline.rs`) loads config and creates the output dir.
7. Without voice replacement it calls `ffmpeg::normalize_to_mp4` and `write_meta`.
8. With replacement it calls `ffmpeg::probe_duration` and `ffmpeg::extract_audio` (progress 5 to 10).
9. Provider `local` runs `local_tts::voice_convert` or `local_tts::speech_to_speech`, chosen by `local_tts_mode`; otherwise `elevenlabs::speech_to_speech` runs.
10. `ffmpeg::replace_audio` writes `voiceover-<timestamp>.mp4`; `write_meta` writes the `.meta.json` file.
11. `cleanup_temp` and `cleanup_stale_recordings` remove temp files; the page sets state `saved` and `libraryStale`.

## Related

- [Frontend Recorder](../building-blocks/frontend-recorder.md)
- [Rust Pipeline and ffmpeg](../building-blocks/rust-pipeline.md)
- [Flow: Local Voice Replacement](local-voice-conversion.md)
- [Events and Channels](../interfaces/events-and-channels.md)
