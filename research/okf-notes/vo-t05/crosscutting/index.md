# Crosscutting

Concerns that span modules.

## Documents

* [Configuration](./configuration.md) - Where settings are defined, stored and read across the layers.
* [Secrets](./secrets.md) - Handling of the ElevenLabs key and Google Drive credentials.
* [Error Handling](./error-handling.md) - How errors are typed, returned and shown across Rust, TypeScript and Python.
* [Logging](./logging.md) - Log output in the frontend, Rust host and Python sidecar.
* [State Management](./state-management.md) - Where UI, session, process and file state are kept.
* [Testing](./testing.md) - Test frameworks, locations and the commands that run them.
* [Security Boundaries](./security-boundaries.md) - Input validation, path restrictions and permission scopes in the code.
