---
id: interfaces/tauri-commands-core
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Commands, Core"
description: "Commands for prerequisites, configuration, recording files and windows."
domain: architecture
tags:
  - interfaces
  - tauri
  - commands
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/lib.rs
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/commands/window.rs
relations:
  relates_to:
    - interfaces/tauri-commands-services
    - interfaces/tauri-events
    - building-blocks/rust-app-shell
---

Registered in `tauri::generate_handler!` (`src-tauri/src/lib.rs`); the webview calls them by name through `invoke`.

| Command | Inputs | Output | Declared in | Called from |
|---|---|---|---|---|
| `check_prerequisites` | none | `PrerequisiteStatus` | `prerequisites.rs` | `src/routes/+layout.svelte` |
| `get_config` | none | `AppConfig` | `config.rs` | `src/lib/state.svelte.ts` |
| `save_config` | `config: AppConfig` | unit | `config.rs` | `src/lib/state.svelte.ts` |
| `save_recording_chunk` | `sessionId`, `chunk` bytes, `chunkIndex` | path string | `commands/recording.rs` | `src/lib/recorder.svelte.ts` |
| `finalize_recording` | `sessionId` | path string | `commands/recording.rs` | `src/lib/recorder.svelte.ts` |
| `get_temp_dir` | none | string | `commands/recording.rs` | no call in `src/` |
| `read_file_bytes` | `path` | bytes | `commands/recording.rs` | `src/routes/preview/+page.svelte` |
| `create_widget_window` | none | unit | `commands/window.rs` | no call in `src/` |
| `close_widget_window` | none | unit | `commands/window.rs` | `src/routes/widget/+page.svelte` |

Every command returns `Result<_, String>` except `get_temp_dir`, which returns a `String`.

Capabilities for the `main` and `widget` windows are in `src-tauri/capabilities/default.json`.

## Related

- [Tauri commands, services](tauri-commands-services.md)
- [Tauri events and channels](tauri-events.md)
- [Rust app shell](../building-blocks/rust-app-shell.md)
