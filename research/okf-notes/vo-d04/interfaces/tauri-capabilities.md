---
id: interfaces/tauri-capabilities
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Tauri capabilities"
description: "The permission set granted to the main and widget windows."
domain: architecture
tags:
  - interfaces
  - permissions
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: interfaces
sources:
  - resource: src-tauri/capabilities/default.json
related:
  - deployment/build-and-package
  - interfaces/tauri-commands
---

# Tauri capabilities

`src-tauri/capabilities/default.json` has identifier `default` and applies to windows `main` and `widget`.

## Facts (src-tauri/capabilities/default.json)
- Core window and webview permissions: create, close, always-on-top, position, size, decorations, show, hide.
- Shell: `shell:allow-execute`, `allow-spawn`, `allow-kill`, plus an execute entry for command `ffmpeg`.
- Dialog: open, save, message, ask.
- Filesystem: `fs:default`, text-file read and write scoped to `$APPDATA/**`, scopes temp, video and home (recursive).
- Global shortcut: default, register, unregister, is-registered.

## Related

- [[deployment/build-and-package]]
- [[interfaces/tauri-commands]]
