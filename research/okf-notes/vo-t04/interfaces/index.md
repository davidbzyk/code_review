# Interfaces

Notes in this folder.

## Documents

* [Tauri commands](./tauri-commands.md) - The backend exposes 14 commands through generate_handler!, each declared with #[tauri::command] and called from the frontend by name.
* [Events and channels](./tauri-events-and-channels.md) - Progress and window control travel as PipelineEvent and DriveEvent channel messages and as three named window events.
* [External HTTP calls](./external-http-apis.md) - The code calls ElevenLabs and Google endpoints from Rust and, in browser mode, from the page.
* [Config schema](./config-schema.md) - AppConfig is the JSON shape stored in config.json and mirrored by the TypeScript AppConfig type.
