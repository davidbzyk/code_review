# crosscutting

Notes in this folder.

* [Configuration handling](./configuration.md) - Config lives in config.json in the app data folder, with a localStorage mirror and a dev-only static file.
* [Error handling](./error-handling.md) - Rust commands return Result<_, String>, the sidecar returns JSON error bodies, and the UI shows messages.
* [Logging](./logging.md) - Rust uses the log crate with tauri-plugin-log, the sidecar uses Python logging, and the UI uses a console logger.
* [Secret handling](./secrets.md) - API key and Drive tokens are kept in the OS keychain and stripped from files and localStorage.
* [State and storage](./state.md) - Where state lives: Svelte store, module variables, Rust managed state, files in app data, and sidecar memory.
* [Testing](./testing.md) - Tests exist for the frontend (vitest), Rust modules (cargo test) and the sidecar (pytest), run by hooks and CI.
