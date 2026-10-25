# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `21d799db2caf42be15514065780e0faadaae83d9` (base) and
`bb090a4a9bf3951afa70d85e4bb727948eeba754` (head). What the change is meant to do:

The change reorganises sidecar HTTP and generation code and routes generated audio through the desktop backend. The Rust side registers one shared HTTP client with per-request timeouts, adds a command that returns generated audio bytes, validates generation ids and waits for sidecar startup by notification instead of polling. The Python server moves generation and voice conversion into separate functions run by the queue, and common page styles move into the global stylesheet. The content security policy no longer allows media from localhost.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
