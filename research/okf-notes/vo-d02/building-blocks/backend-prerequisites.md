---
id: building-blocks/backend-prerequisites
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust prerequisites check
description: Detects whether ffmpeg runs on the system PATH.
domain: architecture
tags:
  - building-block
  - backend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/prerequisites.rs
related:
  - building-blocks/frontend-shell
  - building-blocks/backend-entry
---

src-tauri/src/prerequisites.rs runs `ffmpeg -version` through `std::process::Command`.

## Items
- `check_ffmpeg()`: true when the command exits with success.
- `check_prerequisites` (command): returns `PrerequisiteStatus { ffmpeg_available, ffmpeg_version }`; the version is the first output line.

## Called by
`run()` in src-tauri/src/lib.rs at startup and src/routes/+layout.svelte.

## Related
[[building-blocks/frontend-shell]], [[building-blocks/backend-entry]]
