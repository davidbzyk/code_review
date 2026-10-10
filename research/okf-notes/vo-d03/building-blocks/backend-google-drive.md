---
id: building-blocks/backend-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Backend Google Drive client"
description: "PKCE OAuth flow over a loopback listener, token refresh and file upload to Drive."
domain: architecture
tags:
  - building-block
  - backend
  - google-drive
  - oauth
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - runtime/google-drive-connect
    - runtime/upload-to-drive
---

# Backend Google Drive client

`src-tauri/src/google_drive.rs` implements Google sign-in and upload for the desktop app.

## Items

- Structs `DriveTokens` and enum `DriveEvent` (`Progress { percent }`, `Complete { url }`, `Error { message }`).
- `generate_code_verifier()`: 32 random bytes, base64url. `code_challenge(verifier)`: SHA-256, base64url.
- `google_drive_connect(client_id, client_secret)` (async command): binds `127.0.0.1:0`, opens the consent URL with `open::that`, accepts one callback (120 second timeout, 200 ms polling), reads the `code` query value, exchanges it at `https://oauth2.googleapis.com/token`, computes `expires_at`, fetches the email with `get_user_email`.
- `refresh_access_token(client_id, client_secret, refresh_token)`: refresh-token grant; not registered as a command.
- `upload_to_drive(access_token, file_path, on_event)` (async command): multipart upload via `build_multipart_body`, then a permission `{type: anyone, role: reader}`, returns `webViewLink`.
- `google_drive_disconnect()` (command): returns `Ok(())` and does nothing else.

## Called by

`src/routes/settings/+page.svelte` and `src/routes/preview/+page.svelte`.

## Related

- [runtime/google-drive-connect](../runtime/google-drive-connect.md)
- [runtime/upload-to-drive](../runtime/upload-to-drive.md)
- [interfaces/external-http-apis](../interfaces/external-http-apis.md)
- [crosscutting/secrets](../crosscutting/secrets.md)
