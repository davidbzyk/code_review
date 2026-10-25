# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `3f2a14268a65847b7cc5a8961eb7fb8a4bf575b1` (base) and
`9afeb65d8f0b0262250a7e8a11f146f4bf0e1eb1` (head). What the change is meant to do:

The change adds a bundled local text-to-speech sidecar that replaces the dependency on an external local voice server. A Python service handles transcription, voice profiles, chunked speech generation, model downloads and YouTube audio extraction, while the Rust backend starts, health-checks and stops it on a managed port and exposes commands to reach it. The frontend client, home, settings and create-voice screens route through these commands, and the build and CI setup include the sidecar binary.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
