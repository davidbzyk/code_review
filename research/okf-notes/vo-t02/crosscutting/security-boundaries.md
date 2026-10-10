---
id: crosscutting/security-boundaries
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Security Boundaries"
description: "The content security policy, capability permissions and file path rules."
domain: architecture
tags:
  - crosscutting
  - security
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/capabilities/default.json
  - resource: src-tauri/src/commands/recording.rs
  - resource: src-tauri/Info.plist
related:
  - deployment/build-and-package
  - building-blocks/backend-entry-and-commands
---
# Security Boundaries

Three config layers limit what the webview can reach.

## Content security policy (src-tauri/tauri.conf.json)
`connect-src` lists `'self'`, https://api.elevenlabs.io, https://oauth2.googleapis.com, https://www.googleapis.com, https://accounts.google.com, `blob:` and `mediastream:`. `script-src` is `'self' blob:`.

## Capabilities (src-tauri/capabilities/default.json)
- Windows `main` and `widget`.
- Window permissions: create, close, always-on-top, position, size, decorations, show, hide, minimize, unminimize, focus.
- Shell execute is scoped to the sidecar `binaries/ffmpeg` with `args: true`.
- `fs:allow-read-text-file` and `fs:allow-write-text-file` are scoped to `$APPDATA/**`.
- Global shortcut register, unregister and is-registered.

## Path rules (src-tauri/src/commands/recording.rs)
- `read_file_bytes` canonicalizes the path and allows only the temp dir, the video dir, and `~/VoiceOver`.
- `validate_session_id` blocks path separators in session ids.

## Related
- [Build and Package](../deployment/build-and-package.md)
- [Backend Entry and Commands](../building-blocks/backend-entry-and-commands.md)
