---
id: building-blocks/rust-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Google Drive
description: OAuth2 PKCE connection flow and file upload for Google Drive.
domain: architecture
tags:
  - building-block
  - rust
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/google_drive.rs
related:
  - runtime/google-drive-connect-upload
  - interfaces/external-http-apis
  - crosscutting/secrets
  - building-blocks/frontend-integrations
---

# Rust Google Drive

`google_drive.rs` implements three commands: connect, upload and disconnect.

## Facts

- `google_drive_connect(client_id, client_secret)` returns `DriveTokens { access_token, refresh_token, email, connected, expires_at }`.
- `generate_code_verifier` makes 32 random bytes in URL-safe base64; `code_challenge` is SHA-256 of the verifier.
- A `TcpListener` on `127.0.0.1:0` receives the redirect; the wait is 120 seconds.
- The `state` value is compared with the callback's `state`.
- Scope is `https://www.googleapis.com/auth/drive.file` plus `email`.
- `get_user_email` calls `https://www.googleapis.com/oauth2/v2/userinfo`.
- `refresh_access_token` posts to `https://oauth2.googleapis.com/token`.
- `upload_to_drive(access_token, file_path, on_event)` canonicalizes the path, rejects `..`, posts a multipart body built by `build_multipart_body`, and sends `DriveEvent` values `Progress`, `Complete { url }`, `Error`.
- `google_drive_disconnect` calls `secrets::clear_secrets`.

## Calls

`open::that` opens the system browser.

## Related

- [Flow: Connect and Upload to Google Drive](../runtime/google-drive-connect-upload.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
- [Secrets](../crosscutting/secrets.md)
- [Frontend Integrations](./frontend-integrations.md)
