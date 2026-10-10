---
id: building-blocks/rust-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Google Drive"
description: "OAuth2 PKCE sign-in, token refresh helper and file upload to Google Drive."
domain: architecture
tags:
  - building-blocks
  - rust
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - runtime/drive-oauth-connect
    - runtime/drive-upload
    - building-blocks/frontend-drive-logger
    - building-blocks/rust-secrets
---

The Google Drive module implements the loopback OAuth flow and the multipart upload.

## Facts

- Types: `DriveTokens`, and `DriveEvent` with `Progress { percent }`, `Complete { url }`, `Error { message }` (`src-tauri/src/google_drive.rs`).
- `generate_code_verifier()` makes 32 random bytes, base64url encoded; `code_challenge(verifier)` is the SHA-256 digest, base64url encoded.
- `google_drive_connect(client_id, client_secret)` is described step by step in [Drive OAuth flow](../runtime/drive-oauth-connect.md).
- `get_user_email` reads the `email` field from `https://www.googleapis.com/oauth2/v2/userinfo`.
- `refresh_access_token` posts a refresh grant to the Google token endpoint; it is marked `#[allow(dead_code)]` and the app refreshes tokens in `src/lib/drive.ts` instead.
- `upload_to_drive(access_token, file_path, on_event)` reads the file, posts `uploadType=multipart` to the Drive upload endpoint with a body from `build_multipart_body` (boundary `voiceover_boundary`), and returns `webViewLink`. Progress events: 10, 80, 95, then `Complete`.
- `google_drive_disconnect()` calls `secrets::clear_secrets()`.

## Related

- [Drive upload flow](../runtime/drive-upload.md)
- [Frontend drive helper and logger](frontend-drive-logger.md)
- [Rust secrets](rust-secrets.md)
