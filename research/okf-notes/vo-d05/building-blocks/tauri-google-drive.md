---
id: building-blocks/tauri-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Rust Google Drive module
description: google_drive.rs runs the OAuth loopback flow with PKCE and uploads a file to Drive.
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
related:
  - runtime/drive-connect-and-upload
  - building-blocks/frontend-state
  - crosscutting/secrets
---

# Rust Google Drive module

`google_drive.rs` exposes three commands: `google_drive_connect`, `google_drive_disconnect`, `upload_to_drive`.

## Facts

- `google_drive_connect(client_id, client_secret)` builds a PKCE verifier and S256 challenge, opens the consent URL with `open::that`, listens on `127.0.0.1:0` for the redirect (120 s timeout), checks the `state` value, exchanges the code at `https://oauth2.googleapis.com/token`, reads the email from `userinfo`, and returns `DriveTokens`.
- Scope requested: `drive.file` and `email`.
- `refresh_access_token` posts a refresh grant (marked `allow(dead_code)`).
- `upload_to_drive(access_token, file_path, on_event)` canonicalizes the path, rejects `..`, posts a multipart body built by `build_multipart_body`, and returns `webViewLink`; `DriveEvent` carries `Progress`, `Complete`, `Error`.
- `google_drive_disconnect` calls `secrets::clear_secrets()`.

## Uses

- Secrets handling in [[crosscutting/secrets]]; the flow is in [[runtime/drive-connect-and-upload]].

## Related

- [[runtime/drive-connect-and-upload]] - Google Drive connect and upload
- [[building-blocks/frontend-state]] - Frontend state and Drive client
- [[crosscutting/secrets]] - Secret handling
