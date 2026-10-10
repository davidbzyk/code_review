---
id: glossary/backend-terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Glossary, Backend Terms"
description: "Terms used in the Rust code and configuration."
domain: architecture
tags:
  - glossary
  - backend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/config.rs
  - resource: src-tauri/src/secrets.rs
  - resource: src-tauri/src/pipeline.rs
  - resource: src-tauri/src/google_drive.rs
  - resource: src-tauri/src/elevenlabs.rs
  - resource: src-tauri/src/ffmpeg.rs
  - resource: src-tauri/tauri.conf.json
relations:
  relates_to:
    - glossary/frontend-terms
    - building-blocks/rust-config
---

Each line gives the term and its defining file.

- `AppConfig` - Rust struct of the settings (`src-tauri/src/config.rs`).
- `Voice` - voice id, name, description and default flag (`src-tauri/src/config.rs`).
- `WebcamPosition` - `bottom-left` or `bottom-right` (`src-tauri/src/config.rs`).
- `Vault` - JSON blob of four secrets in one keychain entry (`src-tauri/src/secrets.rs`).
- `PipelineEvent` - progress, complete and error messages (`src-tauri/src/pipeline.rs`).
- `DriveEvent` - upload progress messages (`src-tauri/src/google_drive.rs`).
- `DriveTokens` - tokens returned by the OAuth flow (`src-tauri/src/google_drive.rs`).
- S2S - speech-to-speech endpoint, `S2S_BASE_URL` (`src-tauri/src/elevenlabs.rs`).
- PKCE - code verifier and S256 challenge (`generate_code_verifier`, `code_challenge`, `src-tauri/src/google_drive.rs`).
- sidecar - bundled ffmpeg declared in `externalBin` (`src-tauri/tauri.conf.json`); resolved by `resolve_ffmpeg_path` (`src-tauri/src/ffmpeg.rs`).
- chunk - one `chunk_NNNN.webm` file (`src-tauri/src/commands/recording.rs`).

## Related

- [Glossary, frontend terms](frontend-terms.md)
- [Rust config](../building-blocks/rust-config.md)
