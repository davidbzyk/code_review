---
id: building-blocks/icon-tooling
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Icon Tooling"
description: "The Python script that draws the app icon and writes icon files."
domain: architecture
tags:
  - building-block
  - tooling
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: scripts/generate-icon.py
related:
  - deployment/build-and-package
---
# Icon Tooling

`scripts/generate-icon.py` draws a microphone icon with Pillow and writes the icon set that `tauri.conf.json` lists.

## Facts
- Imports `PIL.Image`, `PIL.ImageDraw`, `subprocess`, `shutil`, `os` (scripts/generate-icon.py).
- `ICON_DIR` is `src-tauri/icons` relative to the script.
- `draw_microphone(size=1024)` draws the master image; `main()` writes PNG sizes, `icon.ico` and an `icon.iconset` folder.
- The ICNS step uses `iconutil` (script comment: "using iconutil").
- Colours: background `#0f172a`, microphone `#f97316`.
- Icon paths named in the bundle config: `icons/32x32.png`, `icons/128x128.png`, `icons/128x128@2x.png`, `icons/icon.icns`, `icons/icon.ico` (src-tauri/tauri.conf.json).

## Related
- [Build and Package](../deployment/build-and-package.md)
