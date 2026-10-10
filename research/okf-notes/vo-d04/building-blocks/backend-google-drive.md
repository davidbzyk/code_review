---
id: building-blocks/backend-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend Google Drive client"
description: "OAuth PKCE loopback connect, token refresh helper and file upload."
domain: architecture
tags:
  - backend
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src-tauri/src/google_drive.rs
related:
  - runtime/google-drive-connect-flow
  - runtime/google-drive-upload-flow
  - interfaces/external-http-apis
  - interfaces/pipeline-events
---

# Backend Google Drive client

`src-tauri/src/google_drive.rs` connects a Google account and uploads the output file.

## Items (src-tauri/src/google_drive.rs)
- Structs `DriveTokens`, enum `DriveEvent` (`Progress`, `Complete`, `Error`).
- `generate_code_verifier()`, `code_challenge()` (SHA-256, base64url).
- `google_drive_connect(client_id, client_secret)` (command): returns `DriveTokens`.
- `get_user_email()`, `refresh_access_token()` (a public function with no caller in src-tauri/src).
- `upload_to_drive(access_token, file_path, on_event)` (command): returns the `webViewLink`.
- `build_multipart_body()`: multipart/related body with boundary `voiceover_boundary`.
- `google_drive_disconnect()` (command): returns `Ok(())` and does nothing else.

## Related

- [[runtime/google-drive-connect-flow]]
- [[runtime/google-drive-upload-flow]]
- [[interfaces/external-http-apis]]
- [[interfaces/pipeline-events]]
