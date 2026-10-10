# Building Blocks

One note per layer or module group: responsibility, files, exposed functions, callees.

## Documents

* [Frontend Drive Helper and Logger](./frontend-drive-logger.md) - Browser-side Google token refresh and upload, plus the console logger.
* [Frontend Recorder](./frontend-recorder.md) - Browser media capture, webcam compositing and chunk delivery.
* [Frontend State and Bridges](./frontend-state.md) - The AppState store, the Tauri invoke wrapper, the blob store and the lib barrel file.
* [Icon Script](./icon-script.md) - A Python script that draws the app icon and builds icon files.
* [Preview Route](./route-preview.md) - The page at /preview that plays the recording, processes it and uploads the result.
* [Record Route](./route-record.md) - The home page at / where capture mode is chosen and recording is started, paused or stopped.
* [Settings Route](./route-settings.md) - The page at /settings for the API key, voices and Google Drive connection.
* [Route Shell and Static Assets](./route-shell.md) - Root layout, SvelteKit page options, HTML template, CSS and type declarations.
* [Widget Route](./route-widget.md) - The page at /widget shown in the small recording window.
* [Rust App Shell](./rust-app-shell.md) - The Tauri entry point that registers plugins and the command handlers.
* [Rust Config](./rust-config.md) - Persistent app configuration stored as config.json in the app data directory.
* [Rust ElevenLabs Client](./rust-elevenlabs.md) - HTTP client for the ElevenLabs speech-to-speech and user endpoints.
* [Rust ffmpeg and Prerequisites](./rust-ffmpeg.md) - Resolution of the ffmpeg binary and the three ffmpeg invocations the pipeline uses.
* [Rust Google Drive](./rust-google-drive.md) - OAuth2 PKCE sign-in, token refresh helper and file upload to Google Drive.
* [Rust Pipeline](./rust-pipeline.md) - The process_recording command that turns a recorded WebM into a final MP4.
* [Rust Recording Commands](./rust-recording-commands.md) - Commands that store recording chunks on disk, join them and read files back for preview.
* [Rust Secrets](./rust-secrets.md) - Keychain storage of API key and Google tokens through one JSON entry.
* [Rust Window Commands](./rust-window-commands.md) - Commands that open and close the small always-on-top recording widget window.
