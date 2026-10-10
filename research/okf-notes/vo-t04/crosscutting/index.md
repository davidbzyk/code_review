# Crosscutting

Notes in this folder.

## Documents

* [Configuration](./configuration.md) - Settings live in config.json under app data, in localStorage, and in an ignored static/_config.json used by the dev server.
* [Error handling](./error-handling.md) - Rust commands return Result<_, String> and the frontend turns thrown errors into messages shown on the page.
* [Logging](./logging.md) - Rust uses the log crate with tauri-plugin-log in debug builds, and the frontend uses the logger object over console.
* [Secrets handling](./secrets-handling.md) - The ElevenLabs key and Google client credentials and tokens are stored in the config and masked in logs.
* [State management](./state-management.md) - A single AppState class holds recording, processing and config state in Svelte runes, and module variables hold the live recorders.
* [Testing](./testing.md) - Vitest runs the TypeScript unit tests in jsdom, cargo test runs the in-file Rust tests, and lefthook runs both before each commit.
