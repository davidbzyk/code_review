---
id: interfaces/tauri-commands-recording-and-pipeline
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Commands: Recording and Pipeline"
description: "Commands for recording files, windows, prerequisites and processing."
domain: architecture
tags:
  - interfaces
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/lib.rs
  - resource: src/lib/recorder.svelte.ts
  - resource: src/routes/preview/+page.svelte
related:
  - interfaces/tauri-commands-providers
  - interfaces/events-and-channels
  - runtime/record-flow
---
# Tauri Commands: Recording and Pipeline

These commands are registered in `generate_handler!` (src-tauri/src/lib.rs).

| Command | Inputs | Returns | Declared in | Called from |
|---|---|---|---|---|
| `save_recording_chunk` | `session_id`, `chunk: Vec<u8>`, `chunk_index: u32` | `Result<String, String>` (chunk path) | commands/recording.rs | src/lib/recorder.svelte.ts |
| `finalize_recording` | `session_id` | `Result<String, String>` (WebM path) | commands/recording.rs | src/lib/recorder.svelte.ts |
| `get_temp_dir` | none | `String` | commands/recording.rs | no caller in src |
| `read_file_bytes` | `path` | `Result<Vec<u8>, String>` | commands/recording.rs | src/routes/preview/+page.svelte |
| `create_widget_window` | `app` | `Result<(), String>` | commands/window.rs | no caller in src |
| `close_widget_window` | `app` | `Result<(), String>` | commands/window.rs | src/routes/widget/+page.svelte |
| `check_prerequisites` | none | `PrerequisiteStatus` (`ffmpeg_available`, `ffmpeg_version`) | prerequisites.rs | src/routes/+layout.svelte |
| `process_recording` | `recording_path`, `voice_replacement`, `voice_id`, `on_event: Channel<PipelineEvent>` | `Result<String, String>` (MP4 path) | pipeline.rs | src/routes/preview/+page.svelte |

Rust files sit under src-tauri/src/.

## Related
- [Tauri Commands: Config, Providers and Drive](./tauri-commands-providers.md)
- [Events and Channels](./events-and-channels.md)
- [Record Flow](../runtime/record-flow.md)
