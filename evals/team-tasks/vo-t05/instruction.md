# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `ae7315cffaf8c190c80dc6c3288f4d14c0d6ac4e` (base) and
`6e16cfae8882cba5ba1f59edb4d434c74513185a` (head). What the change is meant to do:

The change adds a Library screen and a sidebar layout for browsing past recordings. The Rust backend lists recordings with sizes, dates, thumbnails and metadata, and offers commands to generate thumbnails, delete, open and reveal files; the pipeline and Drive upload write a companion metadata file with voice and share-link details. Existing pages move under a shared layout with a sidebar and status bar, and the main window is made wider.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
