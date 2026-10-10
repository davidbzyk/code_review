---
id: deployment/build-and-packaging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Build and Packaging
description: Scripts and config files that build, package and sign the app and the sidecar.
domain: architecture
tags:
  - deployment
  - build
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/tauri.conf.json
  - resource: scripts/build-sidecar.sh
  - resource: scripts/generate-icon.py
  - resource: src-tauri/sidecar/voiceover-tts.spec
  - resource: src-tauri/entitlements.plist
  - resource: src-tauri/Info.plist
  - resource: src-tauri/sidecar/entitlements.plist
  - resource: lefthook.yml
  - resource: vite.config.ts
  - resource: svelte.config.js
  - resource: src-tauri/capabilities/default.json
relations:
  relates_to:
    - context/system-context
    - solution-strategy/technology-choices
    - runtime/sidecar-startup
    - crosscutting/testing
---
# Build and Packaging

The app is built with pnpm and Tauri; the sidecar is frozen with PyInstaller first.

## Commands

- `pnpm dev` runs `vite dev`; `pnpm build` runs `vite build` (`package.json`).
- `beforeDevCommand` is `pnpm dev` and `beforeBuildCommand` is `pnpm build`; `frontendDist` is `../build` (`src-tauri/tauri.conf.json`).
- `scripts/build-sidecar.sh [--skip-tests]` activates `.sidecar-venv`, runs `pyinstaller voiceover-tts.spec --noconfirm --clean` in `src-tauri/sidecar`, runs `test_binary.sh`, and copies the binary to `src-tauri/binaries/voiceover-tts-aarch64-apple-darwin`.
- `scripts/generate-icon.py` draws a microphone icon with Pillow into `src-tauri/icons`.
- `vite.config.ts` has `stripConfigPlugin`, which deletes `build/_config.json` after the bundle closes.

## Packaging

- `bundle.externalBin` lists `binaries/ffmpeg` and `binaries/voiceover-tts`; targets are `all`; macOS uses hardened runtime and `entitlements.plist`, minimum system version 11.0.
- The spec file `voiceover-tts.spec` builds from `server.py` and collects `mlx`, `mlx_metal`, `qwen_tts` and other packages.
- `src-tauri/Info.plist` holds camera, microphone and screen-capture usage descriptions.
- `lefthook.yml` defines pre-commit tests and type check, and pre-push clippy and audits.

## Related

- [System Context](../context/system-context.md)
- [Technology Choices](../solution-strategy/technology-choices.md)
- [Flow: Sidecar Startup and Health](../runtime/sidecar-startup.md)
- [Testing](../crosscutting/testing.md)
