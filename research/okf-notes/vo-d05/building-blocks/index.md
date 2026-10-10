# building-blocks

Notes in this folder.

* [Build and tooling scripts](./build-scripts.md) - Two scripts in scripts/ build the sidecar binary and generate the app icon.
* [Frontend recorder and overlays](./frontend-recorder.md) - Browser media capture logic plus the region selector and webcam bubble components.
* [Frontend routes](./frontend-routes.md) - The SvelteKit pages: record, preview, settings, create-voice wizard and the recording widget.
* [Frontend shell and utilities](./frontend-shell.md) - Shared frontend files: HTML shell, global CSS, layout, Tauri invoke wrapper, blob store and logger.
* [Frontend state and Drive client](./frontend-state.md) - Reactive application state with config loading and saving, plus a browser-side Google Drive client.
* [Voicebox client](./frontend-voicebox-client.md) - VoiceboxClient is the frontend wrapper that reaches the local TTS sidecar through Tauri commands.
* [Sidecar engine modules](./sidecar-engine.md) - tts.py, chunked_tts.py and profiles.py hold the model calls, audio assembly and voice profile storage.
* [Sidecar server](./sidecar-server.md) - server.py is the FastAPI app that exposes transcription, generation, profiles and model routes.
* [Rust config and secrets](./tauri-config-secrets.md) - AppConfig is stored as config.json in the app data folder while secrets live in the OS keychain.
* [Tauri core](./tauri-core.md) - The Rust entry point registers plugins, startup tasks and every command handler.
* [Rust Google Drive module](./tauri-google-drive.md) - google_drive.rs runs the OAuth loopback flow with PKCE and uploads a file to Drive.
* [Rust local TTS bridge](./tauri-local-tts-bridge.md) - local_tts.rs, models.rs and sidecar.rs start the Python sidecar and forward requests to it over loopback HTTP.
* [Rust media pipeline](./tauri-media-pipeline.md) - process_recording drives audio extraction, voice transformation and re-muxing through ffmpeg.rs, elevenlabs.rs and local_tts.rs.
* [Rust recording commands](./tauri-recording.md) - Rust commands store recording chunks in a temp folder, join them, serve file bytes and manage the widget window.
