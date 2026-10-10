---
id: solution-strategy/technologies
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Technologies and Structural Decisions"
description: "Languages, frameworks and the split between the SvelteKit webview and the Rust backend."
domain: architecture
tags:
  - solution-strategy
  - technology
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: src-tauri/Cargo.toml
  - resource: svelte.config.js
  - resource: vite.config.ts
  - resource: tsconfig.json
  - resource: pnpm-workspace.yaml
  - resource: src-tauri/tauri.conf.json
relations:
  relates_to:
    - context/system-context
    - deployment/build-and-package
---

The app is a Tauri 2 shell around a statically built SvelteKit front end, with Rust handling files, secrets, ffmpeg and HTTP.

## Technologies

| Technology | Evidence |
|---|---|
| TypeScript, strict mode | `tsconfig.json` |
| Svelte 5 with runes | `package.json` (`svelte`), `svelte.config.js` |
| SvelteKit 2 with `adapter-static` | `package.json`, `svelte.config.js` |
| Vite 7, dev port 5170 | `package.json`, `vite.config.ts` |
| Tauri 2 | `src-tauri/Cargo.toml`, `src-tauri/tauri.conf.json` |
| Rust 2021 edition, `rust-version` 1.77.2 | `src-tauri/Cargo.toml` |
| tokio, reqwest, serde | `src-tauri/Cargo.toml` |
| keyring crate | `src-tauri/Cargo.toml` |
| ffmpeg.wasm packages | `package.json` (`@ffmpeg/*`) |
| pnpm | `pnpm-workspace.yaml`, `package.json` scripts |
| Vitest, jsdom | `package.json`, `vitest.config.ts` |

## Structural decisions

- Two processes: the webview (`src/`) and the Rust backend (`src-tauri/src/`) connected by `invoke`.
- The pages set `ssr = false` and `prerender = true`; the build is static.
- The recorder, preview, settings and config code check `isTauri()` and branch to a browser path.
- Secrets go to the keychain; the config file holds the rest.

## Related

- [System context](../context/system-context.md)
- [Build and package](../deployment/build-and-package.md)
