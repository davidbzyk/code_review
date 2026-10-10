---
id: runtime/upload-recording-to-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Connect and Upload to Google Drive
description: OAuth connection and the upload from the library card.
domain: architecture
tags:
  - runtime
  - flow
  - drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/(app)/settings/+page.svelte
  - resource: src-tauri/src/google_drive.rs
  - resource: src/lib/RecordingCard.svelte
  - resource: src/lib/drive.ts
relations:
  relates_to:
    - building-blocks/rust-google-drive
    - building-blocks/frontend-service-clients
    - building-blocks/frontend-components
---
# Flow: Connect and Upload to Google Drive

This flow connects a Google account and uploads one finished recording.

1. `connectDrive` in the settings page invokes `google_drive_connect` with the client id and secret.
2. `google_drive_connect` (`src-tauri/src/google_drive.rs`) opens the consent URL, waits on a loopback listener, checks `state`, and exchanges the code for tokens.
3. The page merges the returned tokens into `appState.config.google_drive` and calls `saveConfig`.
4. `handleUploadToDrive` in `src/lib/RecordingCard.svelte` checks `expires_at`; when past, it calls `refreshDriveToken` in `src/lib/drive.ts`.
5. It invokes `upload_to_drive` with the token, the file path and a `Channel`.
6. `upload_to_drive` canonicalizes the path, reads the file, posts to the Drive upload URL, and sends `DriveEvent` messages.
7. On success it writes `driveUrl` and `uploadedAt` into the `.meta.json` file and returns `webViewLink`.
8. The card calls `libraryState.updateRecordingMeta`.
9. `disconnectDrive` in the settings page clears the token fields and saves config.

## Related

- [Rust Google Drive](../building-blocks/rust-google-drive.md)
- [Frontend Service Clients](../building-blocks/frontend-service-clients.md)
- [Frontend Components and Styles](../building-blocks/frontend-components.md)
