---
id: building-blocks/backend-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Google Drive module
description: OAuth2 PKCE loopback sign-in and multipart upload to Google Drive.
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
  - runtime/drive-connect
  - runtime/drive-upload
  - interfaces/external-http-apis
  - crosscutting/configuration-and-secrets
---

src-tauri/src/google_drive.rs holds three commands, two event and token types and PKCE helpers.

## Items
- `DriveTokens`: `access_token`, `refresh_token`, `email`, `connected`, `expires_at`.
- `DriveEvent` enum: `Progress { percent }`, `Complete { url }`, `Error { message }`.
- `generate_code_verifier` (32 random bytes, URL-safe base64), `code_challenge` (SHA-256).
- `google_drive_connect(client_id, client_secret)` (command).
- `get_user_email`, `refresh_access_token` (a public function; no caller inside src-tauri/src).
- `upload_to_drive(access_token, file_path, on_event)` (command).
- `build_multipart_body`.
- `google_drive_disconnect` (command): returns `Ok(())` and changes nothing.

## Scope
The authorisation URL requests `https://www.googleapis.com/auth/drive.file email` with `access_type=offline` and `prompt=consent`.

## Related
[[runtime/drive-connect]], [[runtime/drive-upload]], [[interfaces/external-http-apis]], [[crosscutting/configuration-and-secrets]]
