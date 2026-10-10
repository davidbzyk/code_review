---
id: building-blocks/rust-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Rust Google Drive module"
description: "OAuth2 with PKCE over a loopback listener, plus a multipart Drive upload."
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
related:
  - runtime/google-drive-connect-and-upload
  - building-blocks/frontend-clients
  - building-blocks/rust-config-and-secrets
---
# Rust Google Drive module

`google_drive.rs` connects an account and uploads finished videos.

## Items

- Types `DriveTokens` and `DriveEvent` (`Progress`, `Complete`, `Error`).
- `generate_code_verifier`, `code_challenge` (S256 over SHA-256, base64url).
- `google_drive_connect(client_id, client_secret)` returns `DriveTokens`.
- `get_user_email` reads `https://www.googleapis.com/oauth2/v2/userinfo`.
- `refresh_access_token` (marked `allow(dead_code)`).
- `upload_to_drive(access_token, file_path, on_event)` returns the `webViewLink`.
- `build_multipart_body` builds a `multipart/related` body with boundary `voiceover_boundary`.
- `google_drive_disconnect` calls `secrets::clear_secrets`.

## Scope

The consent URL asks for `drive.file` and `email`. The upload code carries a comment that files are not shared publicly.

## Related

- [[runtime/google-drive-connect-and-upload]]
- [[building-blocks/frontend-clients]]
- [[building-blocks/rust-config-and-secrets]]
