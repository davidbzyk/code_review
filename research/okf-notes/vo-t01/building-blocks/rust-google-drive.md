---
id: building-blocks/rust-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Google Drive
description: OAuth loopback flow and file upload to Google Drive.
domain: architecture
tags:
  - building-block
  - rust
  - drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - runtime/upload-recording-to-drive
    - building-blocks/frontend-service-clients
    - building-blocks/rust-config-and-secrets
---
# Rust Google Drive

This module connects a Google account and uploads MP4 files to Drive.

## Items

- `DriveTokens` and `DriveEvent` (`Progress`, `Complete`, `Error`).
- `generate_code_verifier` and `code_challenge` build the PKCE pair (S256 over SHA-256).
- `google_drive_connect(client_id, client_secret)`: binds `127.0.0.1:0`, opens the consent URL with `open::that`, waits up to 120 seconds for the callback, checks the `state` value, exchanges the code at `https://oauth2.googleapis.com/token`, and reads the email from the userinfo endpoint.
- `refresh_access_token` is marked `#[allow(dead_code)]`.
- `upload_to_drive(access_token, file_path, on_event)` reads the file and posts a multipart body built by `build_multipart_body`, then writes `driveUrl` and `uploadedAt` into the `.meta.json` companion.
- `google_drive_disconnect` calls `secrets::clear_secrets`.

## Uses

`secrets`, `pipeline::chrono_timestamp`.

## Related

- [Flow: Connect and Upload to Google Drive](../runtime/upload-recording-to-drive.md)
- [Frontend Service Clients](frontend-service-clients.md)
- [Rust Config and Secrets](rust-config-and-secrets.md)
