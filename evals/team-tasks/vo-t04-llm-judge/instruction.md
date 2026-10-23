# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `15fc88055ae2fb059db8e5b001b5807a14fdbcbd` (base) and
`152365b8573f1f24309de7ab6366a5c75b56ed81` (head). What the change is meant to do:

The change adds a webcam overlay to recordings and moves stored credentials into the operating system keychain. The recorder composites the webcam bubble into the recorded video, with a preview bubble that can switch between two corner positions saved in preferences. Config handling saves secrets to the keychain, removes them from the config file and local storage, and limits file reads to allowed folders; the Drive sign-in now carries a state value. It also adds a CI workflow, an icon generator script and an in-memory blob store.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
