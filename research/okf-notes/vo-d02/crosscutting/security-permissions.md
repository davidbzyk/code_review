---
id: crosscutting/security-permissions
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Security permissions and CSP
description: Tauri capabilities, content security policy and input validation present in config and code.
domain: architecture
tags:
  - crosscutting
  - arc42-8
  - security
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/capabilities/default.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/commands/recording.rs
related:
  - deployment/build-and-packaging
  - building-blocks/backend-recording-commands
---

Permissions are declared in a capability file and a CSP string; one Rust command validates its identifier input.

## Facts
- src-tauri/capabilities/default.json: identifier `default`, windows `main` and `widget`, permissions `core:default`, window create, close, show, hide, size, position, always-on-top and decorations, `shell:allow-execute`, `shell:allow-spawn`, `shell:allow-kill`, dialog open, save, message and ask, `fs:default`.
- Text-file read and write are allowed under `$APPDATA/**`; shell execute is scoped to the command named `ffmpeg` with any args; global-shortcut register, unregister and is-registered are allowed.
- CSP in src-tauri/tauri.conf.json: `default-src 'self'`, `script-src 'self' blob:`, `connect-src` listing `api.elevenlabs.io`, `oauth2.googleapis.com`, `www.googleapis.com`, `accounts.google.com`, `cdn.jsdelivr.net` and `blob:`.
- `validate_session_id` in src-tauri/src/commands/recording.rs accepts only alphanumeric, `-` and `_`.

## Related
[[deployment/build-and-packaging]], [[building-blocks/backend-recording-commands]]
