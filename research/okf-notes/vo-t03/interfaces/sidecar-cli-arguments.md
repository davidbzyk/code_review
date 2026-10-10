---
id: interfaces/sidecar-cli-arguments
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Sidecar command-line arguments"
description: "The options the host passes to the sidecar process."
domain: architecture
tags:
  - interface
  - cli
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/src/sidecar.rs
related:
  - runtime/sidecar-startup
  - interfaces/sidecar-http-routes
---
# Sidecar command-line arguments

`main()` in src-tauri/sidecar/server.py parses these options with `argparse`; `start_sidecar_inner` in src-tauri/src/sidecar.rs supplies them.

| Option | Type | Meaning |
|---|---|---|
| `--host` | string, default `127.0.0.1` | bind host |
| `--port` | int, required | bind port |
| `--data-dir` | string, required | data folder (`models`, `profiles`, `cache`, `generations`, `temp`, `logs`) |
| `--parent-pid` | int, required | process id watched by the watchdog |
| `--ffmpeg` | string, default empty | bundled ffmpeg path; its folder is added to `PATH` when the file exists |

The host passes `--port`, `--data-dir`, `--parent-pid` and `--ffmpeg`; it does not pass `--host`.

## Related

- [[runtime/sidecar-startup]]
- [[interfaces/sidecar-http-routes]]
