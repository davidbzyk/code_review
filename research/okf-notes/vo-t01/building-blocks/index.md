# building-blocks

Notes in this folder.

* [Frontend Components and Styles](./frontend-components.md) - Shared Svelte components, global CSS and the HTML shell.
* [Frontend Recorder](./frontend-recorder.md) - Screen, microphone and webcam capture in the webview.
* [Frontend Routes](./frontend-routes.md) - SvelteKit route files that make up the pages of the webview.
* [Frontend Service Clients](./frontend-service-clients.md) - TypeScript clients for the local TTS sidecar and Google Drive.
* [Frontend State and IPC](./frontend-state-and-ipc.md) - Shared reactive state, the Tauri invoke wrapper and the in-memory blob store.
* [Rust App Shell](./rust-app-shell.md) - Tauri builder, plugin setup, startup tasks and small helper modules.
* [Rust Config and Secrets](./rust-config-and-secrets.md) - The AppConfig model, its JSON file, and the keychain vault.
* [Rust Google Drive](./rust-google-drive.md) - OAuth loopback flow and file upload to Google Drive.
* [Rust Local TTS and Sidecar Manager](./rust-local-tts-and-sidecar.md) - Rust code that starts the Python sidecar and talks to it over HTTP.
* [Rust Pipeline and ffmpeg](./rust-pipeline.md) - The process_recording command, the ffmpeg wrapper and the ElevenLabs client.
* [Rust Recording and Library](./rust-recording-and-library.md) - Chunk storage for recordings and the library of finished MP4 files.
* [Sidecar Engine Modules](./sidecar-engine.md) - Speech engines, text chunking, audio assembly and profile storage in Python.
* [Sidecar Server](./sidecar-server.md) - The FastAPI server that hosts transcription, generation, profiles and model downloads.
