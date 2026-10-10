---
id: interfaces/tauri-commands-system
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri Command: check_prerequisites in the layout"
description: "How the root layout uses the prerequisites command and the window label contract."
domain: architecture
tags:
  - interfaces
  - tauri
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+layout.svelte
  - resource: src-tauri/src/prerequisites.rs
  - resource: src-tauri/src/commands/window.rs
  - resource: src-tauri/tauri.conf.json
related:
  - interfaces/tauri-commands-recording-and-pipeline
  - building-blocks/app-shell
---
# Tauri Command: check_prerequisites in the layout

The root layout calls `check_prerequisites` once, after `loadConfig`.

## Facts
- `check_prerequisites` returns `PrerequisiteStatus { ffmpeg_available: bool, ffmpeg_version: Option<String> }` (src-tauri/src/prerequisites.rs).
- The version is the first line of `ffmpeg -version` output.
- `src/routes/+layout.svelte` reads `ffmpeg_available` and sets `appState.ffmpegAvailable`.
- The banner text names `brew install ffmpeg` and `sudo apt install ffmpeg`.
- The window labelled `main` is defined in src-tauri/tauri.conf.json; the window labelled `widget` is built in `create_widget_window` with URL `/widget` (src-tauri/src/commands/window.rs).

## Related
- [Tauri Commands: Recording and Pipeline](./tauri-commands-recording-and-pipeline.md)
- [App Shell](../building-blocks/app-shell.md)
