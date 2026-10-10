---
id: deployment/sidecar-build
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Sidecar Build
description: How the Python sidecar is frozen into the voiceover-tts binary and copied for Tauri.
domain: architecture
tags:
  - deployment
  - sidecar
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: scripts/build-sidecar.sh
  - resource: src-tauri/sidecar/voiceover-tts.spec
  - resource: src-tauri/sidecar/requirements.txt
related:
  - building-blocks/sidecar-server
  - deployment/build-and-packaging
  - building-blocks/rust-sidecar-manager
---

# Sidecar Build

`scripts/build-sidecar.sh [--skip-tests]` produces `src-tauri/binaries/voiceover-tts-aarch64-apple-darwin`.

## Steps in the script

1. Require the venv `.sidecar-venv` (exit 1 with a creation hint if missing) and `source` it.
2. `cd src-tauri/sidecar` and run `pyinstaller voiceover-tts.spec --noconfirm --clean`.
3. Check that `dist/voiceover-tts` exists.
4. Unless `--skip-tests`, run `bash src-tauri/sidecar/test_binary.sh` on it.
5. Copy it to `src-tauri/binaries/voiceover-tts-aarch64-apple-darwin`.

## Spec file

- Entry script `server.py`; the executable name is `voiceover-tts`, `console=True`.
- `collect_all` is used for `mlx`, `mlx_metal`, `qwen_tts`; `copy_metadata` for `safetensors`, `transformers` and others.
- `hiddenimports` include `fastapi`, `uvicorn`, `torch`, `mlx_audio`, `yt_dlp`, `tts`, `profiles`, `chunked_tts`.
- `excludes` lists the `nvidia.*` packages.

## requirements.txt

Pins `fastapi`, `uvicorn`, `python-multipart`, `mlx`, `mlx-whisper`, `mlx-audio`, `huggingface-hub`, `numpy`, `soundfile`, `qwen-tts`, `torch`, `transformers`, `yt-dlp`.

## Related

- [Sidecar Server](../building-blocks/sidecar-server.md)
- [Build and Packaging](./build-and-packaging.md)
- [Rust Sidecar Manager](../building-blocks/rust-sidecar-manager.md)
