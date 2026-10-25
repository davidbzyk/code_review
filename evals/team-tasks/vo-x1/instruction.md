# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `02ac4d2949831e10616c378437beaf866f626f26` (base) and
`1300764111acc28a5c4b093d6577116392173f88` (head). What the change is meant to do:

The change adds a session-id check to the recording commands, an expiry timestamp for Drive tokens, a timeout on the Drive sign-in callback, async video-tool calls and a content security policy in the window config. The frontend shares one environment-detection helper instead of local copies, sends recording chunks as byte arrays, listens for widget stop and cancel events on the home page and refreshes expired Drive tokens before upload. It removes two unused Rust dependencies and blanks credentials in the config file synced to the static folder.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
