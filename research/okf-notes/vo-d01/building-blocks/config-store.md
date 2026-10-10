---
id: building-blocks/config-store
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Config Store"
description: "Backend module that reads and writes the JSON configuration file in the app data directory."
domain: architecture
tags:
  - building-block
  - rust
  - config
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
---
# Config Store

`config.rs` owns the `AppConfig` type and the commands `get_config` and `save_config`.

## Facts
- Types: `Voice`, `Preferences`, `GoogleDrive`, `AppConfig`, all `Serialize` and `Deserialize` (src-tauri/src/config.rs).
- `Preferences::default` sets `default_capture_mode` to `"fullscreen"`, `webcam_enabled` false, `voice_replacement_enabled` true.
- `default_output_dir` returns the video directory (or home directory) joined with `VoiceOver`.
- `config_path` returns `config.json` under `app_data_dir`, creating the directory.
- `get_config` reads the file, or writes and returns `AppConfig::default()` when it is missing.
- `save_config` writes pretty JSON, then calls `sync_to_static`.
- `sync_to_static` walks the ancestors of the executable path for a `static` directory and writes `_config.json` there; it falls back to `./static`.

## Used by
`pipeline::process_recording` calls `config::get_config` (src-tauri/src/pipeline.rs).

## Related
- [[crosscutting/configuration]]
- [[interfaces/config-json-shape]]
- [[building-blocks/tauri-shell]]
