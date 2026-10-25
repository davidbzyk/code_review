# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `966a2d8778fe9a9cadf11431478349771365820f` (base) and
`02b02c9de77c22a11c5e804064acffaf3c326fed` (head). What the change is meant to do:

The change lets the app seed its configuration from a project-level static config file when no saved config exists. The Rust config loader reads that file from the project root if present and writes it to app data, and the sync to the static folder is skipped when no API key is set. On the frontend, the loader accepts a config only if it includes an API key, falls back to the static file otherwise, and saves that config back to app data in the desktop app.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
