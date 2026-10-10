---
id: building-blocks/rust-config
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust config module"
description: "config.rs defines AppConfig and reads and writes config.json in the app data folder."
domain: architecture
tags:
  - building-block
  - rust
  - configuration
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
relations:
  relates_to:
    - crosscutting/configuration
    - runtime/config-load-and-save
    - interfaces/config-schema
---
# Rust config module

The config module is the Rust owner of persisted settings (src-tauri/src/config.rs).

## Types

`Voice`, `Preferences` (defaults: `fullscreen`, webcam off, voice replacement on), `GoogleDrive`, `AppConfig` (`elevenlabs_api_key`, `voices`, `output_dir`, `preferences`, `google_drive`). Fields use `#[serde(default)]`; `output_dir` defaults to `<Videos or home>/VoiceOver`.

## Functions

- `config_path(app)`: `<app_data_dir>/config.json`, folder created if needed.
- `get_config(app)` (command): reads the file; if missing, seeds from `read_static_config()` or defaults and writes the file.
- `read_static_config()`: looks for `static/_config.json` in the executable's ancestors, then in the working directory.
- `save_config(app, config)` (command): writes pretty JSON, then calls `sync_to_static`.
- `sync_to_static(config)`: when the API key is non-empty, writes `static/_config.json` in the first ancestor of the executable that has a `static` folder, else in the working directory.

## Used by

src-tauri/src/pipeline.rs calls `config::get_config`.

## Related

[[crosscutting/configuration]], [[runtime/config-load-and-save]], [[interfaces/config-schema]]
