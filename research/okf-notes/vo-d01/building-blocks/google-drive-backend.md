---
id: building-blocks/google-drive-backend
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Google Drive Backend"
description: "Backend module for the Google OAuth PKCE flow and the Drive upload command."
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
---
# Google Drive Backend

`google_drive.rs` connects a Google account over a loopback redirect and uploads a file to Drive.

## Facts
- Types: `DriveTokens { access_token, refresh_token, email, connected }` and `DriveEvent` (`Progress`, `Complete`, `Error`).
- `generate_code_verifier` makes 32 random bytes, base64url without padding; `code_challenge` is SHA-256 of it (S256).
- `google_drive_connect(client_id, client_secret)` binds `127.0.0.1:0`, opens the consent URL with `open::that`, accepts one connection, reads the `code` query value, answers with an HTML page, posts to the token endpoint, then fetches the email with `get_user_email`.
- `refresh_access_token` posts a `refresh_token` grant.
- `upload_to_drive(access_token, file_path, on_event)` reads the file, posts a multipart body built by `build_multipart_body`, then posts an `anyone`/`reader` permission and returns `webViewLink`.
- `google_drive_disconnect` returns `Ok(())` and does nothing else.

## Related
- [[runtime/connect-google-drive]]
- [[runtime/upload-to-drive]]
- [[interfaces/external-http-apis]]
- [[crosscutting/secrets-handling]]
