# building-blocks notes

## Documents

* [Frontend routes](./frontend-routes.md) - The SvelteKit pages that make up the user interface.
* [Frontend state and utilities](./frontend-state-and-utils.md) - Shared reactive state, the Tauri invoke wrapper, the logger, the blob store and the HTML and CSS shell.
* [Frontend recorder](./frontend-recorder.md) - Screen, microphone and webcam capture, plus the region selector and the webcam bubble.
* [Frontend service clients](./frontend-clients.md) - Browser-side helpers for Google Drive uploads and for the local TTS sidecar.
* [Tauri host entry and window commands](./tauri-host.md) - The Rust crate entry, plugin setup, command registration, widget window commands and the ffmpeg prerequisite check.
* [Rust recording file commands](./rust-recording-files.md) - Chunked recording storage in the system temp folder and guarded file reads.
* [Rust processing pipeline](./rust-pipeline.md) - The process_recording command, the ffmpeg wrapper and the ElevenLabs client.
* [Rust config and secrets](./rust-config-and-secrets.md) - The AppConfig model stored as config.json and the keychain vault for secrets.
* [Rust sidecar client](./rust-sidecar-client.md) - Process management for the TTS sidecar and the Rust-side HTTP clients that call it.
* [Rust Google Drive module](./rust-google-drive.md) - OAuth2 with PKCE over a loopback listener, plus a multipart Drive upload.
* [Sidecar HTTP server](./sidecar-server.md) - The FastAPI app that exposes health, transcription, generation, profile, model and YouTube routes.
* [Sidecar speech engine](./sidecar-engine.md) - Whisper transcription, Qwen voice cloning, profile storage and text chunking.
