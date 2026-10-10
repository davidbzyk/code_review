---
id: crosscutting/input-and-path-validation
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Input and path validation"
description: "Checks applied to identifiers, file paths and OAuth callbacks."
domain: architecture
tags:
  - crosscutting
  - security
  - validation
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/capabilities/default.json
related:
  - building-blocks/rust-recording-files
  - crosscutting/secrets-handling
  - interfaces/external-http-endpoints
---
# Input and path validation

Validation sits at the Rust command boundary.

## Facts

- `validate_session_id` accepts only alphanumeric characters, `-` and `_` (commands/recording.rs).
- `read_file_bytes` canonicalizes the path and compares against three allowed roots (commands/recording.rs).
- `google_drive_connect` generates a random `state` and rejects a callback whose `state` differs (google_drive.rs).
- PKCE S256 challenge protects the code exchange (google_drive.rs).
- The OAuth listener binds `127.0.0.1` only and times out after 120 s.
- The webview `csp` in tauri.conf.json limits `connect-src` to listed hosts.
- `capabilities/default.json` limits `fs:allow-read-text-file` and `fs:allow-write-text-file` to `$APPDATA/**` and shell execution to two named sidecars.
- The sidecar binds `127.0.0.1` by default (`--host`).

## Related

- [[building-blocks/rust-recording-files]]
- [[crosscutting/secrets-handling]]
- [[interfaces/external-http-endpoints]]
