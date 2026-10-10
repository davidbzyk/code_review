---
id: deployment/build-and-package
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Build and Package"
description: "Commands and configuration that build the front end and the Tauri bundle."
domain: architecture
tags:
  - deployment
  - build
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: package.json
  - resource: docs/BUILD.md
  - resource: src-tauri/tauri.conf.json
  - resource: src-tauri/Cargo.toml
  - resource: vite.config.ts
  - resource: svelte.config.js
  - resource: src-tauri/capabilities/default.json
relations:
  relates_to:
    - deployment/ci-and-hooks
    - building-blocks/icon-script
    - solution-strategy/technologies
---

`pnpm tauri build` runs the front end build and packages the app.

## Facts

- `package.json` scripts: `dev` (`vite dev`), `build` (`vite build`), `check` (`svelte-kit sync && svelte-check`), `test`, `test:rust`, `test:all`, coverage variants, `prepare` (`lefthook install`).
- `build` in `src-tauri/tauri.conf.json`: `frontendDist` `../build`, `devUrl` `http://localhost:5170`, `beforeDevCommand` `pnpm dev`, `beforeBuildCommand` `pnpm build`.
- `bundle`: `active` true, `targets` `all`, five icon paths, `externalBin` `binaries/ffmpeg`.
- `docs/BUILD.md` places the ffmpeg binary at `src-tauri/binaries/ffmpeg-aarch64-apple-darwin` or `ffmpeg-x86_64-apple-darwin`, runs `pnpm tauri dev` for development and `pnpm tauri build` for release.
- Documented outputs: `src-tauri/target/release/bundle/macos/VoiceOver.app` and a `.dmg` under `bundle/dmg/`.
- `vite.config.ts` has a plugin `strip-config` that removes `build/_config.json` after the bundle closes.
- `svelte.config.js` uses `adapter-static` with fallback `index.html`.
- `src-tauri/Cargo.toml` sets `crate-type` to `staticlib`, `cdylib`, `rlib`.
- The app window security policy is the `csp` string in `tauri.conf.json`.

## Related

- [CI and hooks](ci-and-hooks.md)
- [Icon script](../building-blocks/icon-script.md)
- [Technologies](../solution-strategy/technologies.md)
