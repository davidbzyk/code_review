---
id: crosscutting/security-boundaries
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Security Boundaries
description: Input validation, path restrictions and permission scopes in the code.
domain: architecture
tags:
  - crosscutting
  - security
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/src/local_tts.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/capabilities/default.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/sidecar/server.py
  - resource: src-tauri/sidecar/profiles.py
related:
  - building-blocks/rust-recording-commands
  - interfaces/commands-sidecar-proxy
  - building-blocks/sidecar-engine
---

# Security Boundaries

Validation appears at each boundary.

## Facts

- `validate_session_id`: alphanumeric, `-`, `_` only (src-tauri/src/commands/recording.rs).
- `read_file_bytes`: path must be inside the temp dir, the video dir or `~/VoiceOver`.
- `validate_generation_id`: ASCII alphanumeric and `-` (src-tauri/src/local_tts.rs).
- `sidecar_fetch` accepts only paths starting with an entry of `ALLOWED_SIDECAR_PATHS`.
- `upload_to_drive` canonicalizes the path and rejects `..`; OAuth uses PKCE S256 and a `state` check (src-tauri/src/google_drive.rs).
- Sidecar: `_validate_path` for `audio_path` and `source_audio_path`; `/extract-youtube` accepts only https URLs on `youtube.com`, `www.youtube.com`, `m.youtube.com`, `youtu.be`; `_validate_profile_id` (profiles.py); the server binds `127.0.0.1` by default.
- Capability file lists window, dialog, fs, shell and global-shortcut permissions for windows `main` and `widget`.
- `app.security.csp` in tauri.conf.json lists allowed `connect-src` hosts.

## Related

- [Rust Recording Commands](../building-blocks/rust-recording-commands.md)
- [Tauri Commands: Local TTS and Sidecar Proxy](../interfaces/commands-sidecar-proxy.md)
- [Sidecar Engine Modules](../building-blocks/sidecar-engine.md)
