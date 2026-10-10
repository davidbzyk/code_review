---
id: deployment/sidecar-packaging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Sidecar packaging"
description: "How the Python sidecar is frozen into the voiceover-tts binary."
domain: architecture
tags:
  - deployment
  - pyinstaller
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/sidecar/voiceover-tts.spec
  - resource: src-tauri/sidecar/requirements.txt
  - resource: src-tauri/sidecar/test_binary.sh
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/src/sidecar.rs
related:
  - building-blocks/sidecar-server
  - runtime/sidecar-startup
  - deployment/build-and-run
---
# Sidecar packaging

The sidecar is built with PyInstaller from a spec file and looked up by the host as `voiceover-tts`.

## Facts

- The spec's docstring gives the build command `pyinstaller voiceover-tts.spec`; the spec analyses `server.py`, names the executable `voiceover-tts` and sets `target_arch="arm64"` (src-tauri/sidecar/voiceover-tts.spec).
- The spec collects `mlx`, `mlx_metal`, `qwen_tts`, `librosa`, `lazy_loader`, `mlx_audio`, copies package metadata, lists hidden imports (including `tts`, `profiles`, `chunked_tts`) and excludes `nvidia` packages.
- Python dependencies are pinned in src-tauri/sidecar/requirements.txt.
- `test_binary.sh` is a test script for the built binary, run before copying it to `binaries/`.
- Tauri bundles it as `externalBin` `binaries/voiceover-tts` (src-tauri/tauri.conf.json).
- At run time `resolve_sidecar_path` looks for `voiceover-tts` next to the main executable (src-tauri/src/sidecar.rs); debug builds use Python source instead.

## Related

- [[building-blocks/sidecar-server]]
- [[runtime/sidecar-startup]]
- [[deployment/build-and-run]]
