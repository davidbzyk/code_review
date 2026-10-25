# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `0b3d1346cb747cee4647c144d91c955f9522cf34` (base) and
`3a944f6c5bd372b00769eeecd950eb180cbc656b` (head). What the change is meant to do:

The change extends the local voice sidecar with a voice-conversion mode alongside text-to-speech, and makes generated audio follow the original recording's timing. The sidecar gains a conversion endpoint, timestamp-aligned segment generation, transcript filtering and path validation; the Rust backend probes video duration, picks the mode from config, saves a transcript next to the output and cleans up stale temporary recordings. It also adds sidecar test suites, a build script and an expanded README.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
