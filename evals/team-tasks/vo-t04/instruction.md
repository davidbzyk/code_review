# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `099656be3d2d779b7908a35e468feb7fe98b0619` (base) and
`b9d28e98158fc7b10366fee4286252ff65a9dc0b` (head). What the change is meant to do:

The change adds a webcam overlay to recordings and moves stored credentials into the operating system keychain. The recorder composites the webcam bubble into the recorded video, with a preview bubble that can switch between two corner positions saved in preferences. Config handling saves secrets to the keychain, removes them from the config file and local storage, and limits file reads to allowed folders; the Drive sign-in now carries a state value. It also adds a CI workflow, an icon generator script and an in-memory blob store.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
