---
id: building-blocks/build-scripts
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Build and tooling scripts
description: Two scripts in scripts/ build the sidecar binary and generate the app icon.
domain: architecture
tags:
  - building-block
  - tooling
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: scripts/build-sidecar.sh
  - resource: scripts/generate-icon.py
  - resource: lefthook.yml
related:
  - deployment/build-and-packaging
  - crosscutting/testing
---

# Build and tooling scripts

The `scripts/` folder holds two standalone tools.

## Facts

- `scripts/build-sidecar.sh [--skip-tests]` activates `.sidecar-venv`, runs `pyinstaller voiceover-tts.spec --noconfirm --clean` in `src-tauri/sidecar`, runs `test_binary.sh` unless skipped, and copies `dist/voiceover-tts` to `src-tauri/binaries/voiceover-tts-aarch64-apple-darwin`.
- `scripts/generate-icon.py` draws a microphone with Pillow (`draw_microphone`) and `main()` writes the icon sizes into `src-tauri/icons`; it calls `iconutil` through `subprocess` for the macOS icon set.
- `lefthook.yml` defines pre-commit and pre-push hook commands (tests, typecheck, clippy, audits).

## Related

- Packaging context is in [[deployment/build-and-packaging]]; hook commands are in [[crosscutting/testing]].

## Related

- [[deployment/build-and-packaging]] - Build and packaging
- [[crosscutting/testing]] - Testing
