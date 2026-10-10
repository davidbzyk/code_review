---
id: crosscutting/permissions-and-csp
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Permissions and content security policy"
description: "Tauri capability file and CSP string that limit what the webview may do."
domain: architecture
tags:
  - crosscutting
  - security
  - arc42-8
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/capabilities/default.json
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/commands/recording.rs
relations:
  relates_to:
    - building-blocks/backend-entry
    - interfaces/external-http-apis
---

# Permissions and content security policy

Two files declare what the webview may call and which hosts it may reach.

## Capability `default` (`src-tauri/capabilities/default.json`)

- Windows: `main` and `widget`.
- Permissions: `core:default`, window create/close/size/position/decorations/show/hide/always-on-top, webview window creation, dialog open/save/message/ask, `fs:default`.
- Text-file read and write allowed under `$APPDATA/**`.
- `shell:allow-execute` limited to command name `ffmpeg` with any args.
- fs scopes: temp, video and home, recursive.
- Global shortcut register, unregister and is-registered.

## CSP (`src-tauri/tauri.conf.json`)

`default-src 'self'`; `script-src 'self' blob:`; `worker-src 'self' blob:`; `connect-src` allows `api.elevenlabs.io`, `oauth2.googleapis.com`, `www.googleapis.com`, `accounts.google.com`, `cdn.jsdelivr.net`, `blob:` and `mediastream:`; `media-src` allows `blob:`, `mediastream:` and `https://asset.localhost`; `img-src` allows `data:` and `blob:`; `style-src 'self' 'unsafe-inline'`.

## Input check in Rust

`validate_session_id` in `src-tauri/src/commands/recording.rs` limits session ids to alphanumerics, `-` and `_`.

## Related

- [building-blocks/backend-entry](../building-blocks/backend-entry.md)
- [interfaces/external-http-apis](../interfaces/external-http-apis.md)
- [deployment/build-and-packaging](../deployment/build-and-packaging.md)
