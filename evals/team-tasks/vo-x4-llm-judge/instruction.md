# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `b957febf3680dbc91ad08b67333b1ff649f997d5` (base) and
`3a0594941a1ae4200d6d532be5ae1a99b58f0201` (head). What the change is meant to do:

The change lets the app seed its configuration from a project-level static config file when no saved config exists. The Rust config loader reads that file from the project root if present and writes it to app data, and the sync to the static folder is skipped when no API key is set. On the frontend, the loader accepts a config only if it includes an API key, falls back to the static file otherwise, and saves that config back to app data in the desktop app.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
