# Project Rules
These are the project's engineering rules. Every change is expected to follow them, and a review may cite a rule by its number.

## Frontend (TypeScript and Svelte)

**R-01.** TypeScript code must compile under `strict` mode without `any`, `@ts-ignore`, or non-null assertions (`!`) unless a comment on the same line gives the reason.

**R-02.** Shared application state lives in one module of runes-based state; components must not keep their own copy of a value that already exists in shared state.

**R-03.** Svelte components must not call Tauri `invoke` or `fetch` directly; they go through a function in `src/lib/` so the call can be mocked in tests.

**R-04.** Any `$effect`, event listener, timer, `MediaRecorder`, or media stream created by a component or module must be released in a cleanup path (effect return, `onDestroy`, or an explicit stop function).

**R-05.** Every `await` on an IPC or network call must sit in a `try/catch` (or `.catch`) that either reports the failure to the user or rethrows; empty catch blocks are not allowed.

## Backend (Rust)

**R-06.** Production Rust code must not use `unwrap()`, `expect()`, or `panic!` outside tests and startup code that cannot recover; fallible functions return `Result` with a typed or string error that reaches the caller.

**R-07.** Tauri commands must validate every path, URL, and identifier received from the frontend before using it, and must not build file paths from unchecked input.

**R-08.** Blocking work (process spawning, file I/O on large files, long waits) must not run directly on the async runtime; use async APIs or `spawn_blocking`.

**R-09.** Every outbound HTTP request must set an explicit timeout and check the response status before reading the body.

**R-10.** Every `unsafe` block needs a `// SAFETY:` comment stating the invariant it relies on.

## Python sidecar

**R-11.** Request bodies and query parameters in the sidecar server must be declared as typed models or typed parameters; handlers must not read raw untyped dictionaries from a request.

**R-12.** Python functions must carry type hints on parameters and return values, and must not use bare `except:` or `except Exception: pass`.

**R-13.** The sidecar must bind only to the loopback interface, and must not log request audio, transcripts, or file contents at INFO level or above.

## Security and secrets

**R-14.** API keys, client secrets, and OAuth tokens must be stored through the secrets module or OS credential store, and must never appear in source, test fixtures, logs, error messages, or the plain config file.

**R-15.** Child processes (ffmpeg, the sidecar) must be started with an argument list, never through a shell string, and any user-supplied value in an argument must be validated first.

## Quality and process

**R-16.** Every new public function, command, or component with logic must have a test in the same change; a bug fix must add a test that fails before the fix.

**R-17.** Application code must log through the project's logger (frontend `logger.ts`, Rust `log`/`tracing`, Python `logging`) with a component prefix; bare `console.log`, `println!`, and `print()` are not allowed outside tests and CLI scripts.

**R-18.** Dependencies must be added with a version range in the manifest and a committed lockfile update; a new dependency needs a one-line justification in the change description.

**R-19.** Formatting, lint, type-check, and test commands defined in `package.json` and the pre-commit hooks must pass before a change is merged; hooks must not be bypassed.

**R-20.** User-visible behavior changes must update the README or docs in the same change.
