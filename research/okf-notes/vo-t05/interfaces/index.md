# Interfaces

Commands, routes and message formats.

## Documents

* [Tauri Commands: App, Config, Recording](./commands-app-config-recording.md) - Commands for prerequisites, config, recording files and the widget window.
* [Tauri Commands: Pipeline, Models, Drive, ElevenLabs](./commands-pipeline-models-drive.md) - Commands for processing a recording, model management, Google Drive and key testing.
* [Tauri Commands: Local TTS and Sidecar Proxy](./commands-sidecar-proxy.md) - Commands in local_tts.rs that reach the Python sidecar.
* [Channels and Window Events](./tauri-events-and-channels.md) - Typed channel messages from Rust to the webview and window events between pages.
* [Sidecar HTTP: Transcribe, Generate, Audio, Convert, YouTube](./sidecar-http-generation.md) - Routes in server.py for speech work.
* [Sidecar HTTP: Profiles and Models](./sidecar-http-profiles-models.md) - Routes in server.py for voice profiles and model files.
* [External HTTP APIs](./external-http-apis.md) - The third-party URLs the code calls, with the files that call them.
