# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `929123b134d41df41a57942ab81376335e18ccbd` (base) and
`34f3aef77486fd1c6666bcb9580ba45b5cd0c128` (head). What the change is meant to do:

The change extends the local voice sidecar with a voice-conversion mode alongside text-to-speech, and makes generated audio follow the original recording's timing. The sidecar gains a conversion endpoint, timestamp-aligned segment generation, transcript filtering and path validation; the Rust backend probes video duration, picks the mode from config, saves a transcript next to the output and cleans up stale temporary recordings. It also adds sidecar test suites, a build script and an expanded README.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
