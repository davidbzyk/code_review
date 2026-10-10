---
id: building-blocks/rust-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Google Drive client"
description: "google_drive.rs runs the OAuth PKCE loopback flow and uploads a file to Drive with a public reader link."
domain: architecture
tags:
  - building-block
  - rust
  - google-drive
  - oauth
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - runtime/drive-connect-flow
    - runtime/drive-upload-flow
    - interfaces/external-http-apis
---
# Rust Google Drive client

The Drive module handles consent, token exchange and upload (src-tauri/src/google_drive.rs).

## Types and helpers

- `DriveTokens { access_token, refresh_token, email, connected, expires_at }`.
- `DriveEvent` (`Progress`, `Complete`, `Error`) serialised as `{event, data}`.
- `generate_code_verifier()` (32 random bytes, base64url) and `code_challenge()` (SHA-256, base64url).
- `get_user_email(client, access_token)`, `refresh_access_token(...)` (marked `#[allow(dead_code)]`), `build_multipart_body(...)`.

## Commands

- `google_drive_connect(client_id, client_secret)`: see [[runtime/drive-connect-flow]].
- `upload_to_drive(access_token, file_path, on_event)`: see [[runtime/drive-upload-flow]].
- `google_drive_disconnect()`: returns `Ok(())` and does nothing else.

## Uses

`reqwest`, `url`, `open`, `rand`, `sha2`, `base64`, `std::net::TcpListener`.

## Related

[[runtime/drive-connect-flow]], [[runtime/drive-upload-flow]], [[interfaces/external-http-apis]]
