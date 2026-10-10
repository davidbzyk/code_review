# Building Blocks

Modules and layers.

## Documents

* [Frontend Routes](./frontend-routes.md) - The five SvelteKit pages and the shared layout that make up the user interface.
* [Frontend State and Config](./frontend-state-and-config.md) - The shared reactive app state, config persistence, logger, blob store and the Tauri invoke wrapper.
* [Frontend Recorder](./frontend-recorder.md) - Screen, microphone and webcam capture with MediaRecorder, plus region selection and the webcam bubble.
* [Frontend Integrations](./frontend-integrations.md) - Browser-side clients for the sidecar (through Tauri) and for the Google Drive HTTP API.
* [Rust App Shell](./rust-app-shell.md) - The Tauri entry point that registers plugins, shared state, startup tasks and every command.
* [Rust Recording Commands](./rust-recording-commands.md) - Commands that store recording chunks in a temp folder, join them, read files back and clean up.
* [Rust Pipeline and ffmpeg](./rust-pipeline.md) - The process_recording command and the ffmpeg wrappers it drives.
* [Rust TTS Providers and Models](./rust-tts-providers.md) - ElevenLabs client, local sidecar client, provider enum and model download commands.
* [Rust Sidecar Manager](./rust-sidecar-manager.md) - Starts, health-checks, restarts and stops the Python TTS child process.
* [Rust Config and Secrets](./rust-config-and-secrets.md) - The persisted AppConfig in config.json and the keychain vault that holds its secrets.
* [Rust Google Drive](./rust-google-drive.md) - OAuth2 PKCE connection flow and file upload for Google Drive.
* [Sidecar Server](./sidecar-server.md) - The FastAPI process that exposes transcription, generation, profiles, models and YouTube extraction.
* [Sidecar Engine Modules](./sidecar-engine.md) - tts.py, chunked_tts.py and profiles.py: speech models, text and audio chunking, and profile storage.
