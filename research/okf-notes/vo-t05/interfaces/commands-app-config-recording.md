---
id: interfaces/commands-app-config-recording
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Tauri Commands: App, Config, Recording
description: Commands for prerequisites, config, recording files and the widget window.
domain: architecture
tags:
  - interface
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/src/lib.rs
related:
  - interfaces/commands-pipeline-models-drive
  - interfaces/commands-sidecar-proxy
  - building-blocks/rust-app-shell
---

# Tauri Commands: App, Config, Recording

All are registered in `generate_handler!` (src-tauri/src/lib.rs).

| Command | Inputs | Output | Declared in | Called from |
|---|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | prerequisites.rs | src/routes/+layout.svelte |
| `get_config` | none | `AppConfig` | config.rs | src/lib/state.svelte.ts |
| `save_config` | `config: AppConfig` | unit | config.rs | src/lib/state.svelte.ts |
| `get_temp_dir` | none | `String` | commands/recording.rs | none found in src/ |
| `save_recording_chunk` | `session_id`, `chunk: Vec<u8>`, `chunk_index: u32` | path `String` | commands/recording.rs | src/lib/recorder.svelte.ts |
| `finalize_recording` | `session_id` | path `String` | commands/recording.rs | src/lib/recorder.svelte.ts |
| `read_file_bytes` | `path` | `Vec<u8>` | commands/recording.rs | src/routes/preview/+page.svelte |
| `create_widget_window` | none | unit | commands/window.rs | not called in src/ |
| `close_widget_window` | none | unit | commands/window.rs | src/routes/widget/+page.svelte |

Errors are `String` values.

## Related

- [Tauri Commands: Pipeline, Models, Drive, ElevenLabs](./commands-pipeline-models-drive.md)
- [Tauri Commands: Local TTS and Sidecar Proxy](./commands-sidecar-proxy.md)
- [Rust App Shell](../building-blocks/rust-app-shell.md)
