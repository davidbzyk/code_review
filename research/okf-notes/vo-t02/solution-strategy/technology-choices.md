---
id: solution-strategy/technology-choices
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Technology Choices"
description: "The languages, frameworks and structural decisions visible in the manifests and config files."
domain: architecture
tags:
  - strategy
  - technology
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: src-tauri/tauri.conf.json
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: tsconfig.json
  - resource: vitest.config.ts
  - resource: src/routes/+layout.ts
  - resource: lefthook.yml
  - resource: pnpm-workspace.yaml
  - resource: scripts/generate-icon.py
  - resource: .npmrc
related:
  - context/system-context
  - deployment/build-and-package
  - building-blocks/backend-entry-and-commands
---
# Technology Choices

The app is a Rust core and a SvelteKit webview joined by Tauri commands.

## Technologies
| Technology | Shown in |
|---|---|
| Tauri 2 (`tauri = "2.10.3"`) | src-tauri/Cargo.toml, src-tauri/tauri.conf.json |
| Rust edition 2021, tokio, reqwest | src-tauri/Cargo.toml |
| Svelte 5 with runes compile option | svelte.config.js, package.json |
| SvelteKit with `adapter-static`, fallback `index.html` | svelte.config.js |
| Vite 7, port 5170, `strictPort` | vite.config.ts |
| TypeScript, `strict: true` | tsconfig.json |
| Vitest with jsdom | vitest.config.ts |
| pnpm, `engine-strict=true` | package.json, .npmrc, pnpm-workspace.yaml |
| ffmpeg sidecar `binaries/ffmpeg` and `@ffmpeg/ffmpeg` (wasm) | src-tauri/tauri.conf.json, package.json |
| `keyring` with apple-native and linux-native | src-tauri/Cargo.toml |
| lefthook git hooks | lefthook.yml |
| Python with Pillow for icons | scripts/generate-icon.py |

## Structural decisions
- Server rendering is off and prerender is on for the route tree (src/routes/+layout.ts).
- Process split: the webview calls Rust through `invoke`; Rust owns files, ffmpeg, keychain, OAuth and HTTP to providers.
- Dual mode: `isTauri()` selects a Tauri path or a browser fallback in the same Svelte code.
- Two voice providers, chosen by `config.provider` (`elevenlabs` or `local`).

## Related
- [System Context](../context/system-context.md)
- [Build and Package](../deployment/build-and-package.md)
- [Backend Entry and Commands](../building-blocks/backend-entry-and-commands.md)
