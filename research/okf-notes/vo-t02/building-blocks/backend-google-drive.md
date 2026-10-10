---
id: building-blocks/backend-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend Google Drive"
description: "OAuth 2.0 PKCE connection and file upload to Google Drive."
domain: architecture
tags:
  - building-block
  - backend
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/google_drive.rs
related:
  - runtime/google-drive-connect
  - runtime/drive-upload
  - interfaces/tauri-commands-providers
---
# Backend Google Drive

This module connects a Google account and uploads the finished file.

## Items (src-tauri/src/google_drive.rs)
- Types `DriveTokens` and `DriveEvent` (`Progress`, `Complete`, `Error`).
- `generate_code_verifier` and `code_challenge` (SHA-256, base64url).
- Commands `google_drive_connect`, `upload_to_drive`, `google_drive_disconnect`.
- `get_user_email` and public `refresh_access_token`; no other file in the tree calls `refresh_access_token`.
- `build_multipart_body` for the upload payload.

## Calls
`secrets::clear_secrets`, `open::that`, `reqwest`.

## Related
- [Google Drive Connect](../runtime/google-drive-connect.md)
- [Drive Upload](../runtime/drive-upload.md)
- [Tauri Commands: Config, Providers and Drive](../interfaces/tauri-commands-providers.md)
