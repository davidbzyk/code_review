# crosscutting

## Documents

- [Configuration](./configuration.md) - Where settings live: config.json, localStorage, static/_config.json and build config files.
- [Error handling](./error-handling.md) - How Rust and TypeScript code report failures to callers and to the user.
- [Logging](./logging.md) - Console logger in the frontend and the log crate with tauri-plugin-log in Rust.
- [Permissions and content security policy](./permissions-and-csp.md) - Tauri capability file and CSP string that limit what the webview may do.
- [Secrets handling](./secrets.md) - Where the ElevenLabs key and Google credentials are held, copied and blanked.
- [State management](./state-management.md) - Shared runes state in AppState plus module-level state in the recorder and Rust temp files.
