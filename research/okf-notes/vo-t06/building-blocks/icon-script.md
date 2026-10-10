---
id: building-blocks/icon-script
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Icon Script"
description: "A Python script that draws the app icon and builds icon files."
domain: architecture
tags:
  - building-blocks
  - tooling
  - python
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: scripts/generate-icon.py
relations:
  relates_to:
    - deployment/build-and-package
---

`scripts/generate-icon.py` is the only Python file; it writes into `src-tauri/icons`.

## Facts

- `ICON_DIR` is `src-tauri/icons` relative to the script (`scripts/generate-icon.py`).
- Colours: background `#0f172a`, microphone `#f97316`, highlight `#fb923c`, ring `#334155`.
- `draw_microphone(size=1024)` draws a rounded square, a capsule microphone body, a highlight stripe and grill lines with `PIL.ImageDraw`.
- `main()` resizes a 1024 pixel master image into PNG files (`icon.png`, `32x32.png`, `128x128.png`, `128x128@2x.png` and Windows store logos), writes `icon.ico` with sizes 16 to 256, and builds `icon.icns` by running `iconutil -c icns` on an iconset directory with `subprocess.run`; it prints a warning when `iconutil` fails.
- The icon file names match the `bundle.icon` list in `src-tauri/tauri.conf.json`.
- The script is not called from `package.json` scripts, CI or `lefthook.yml`.

## Related

- [Build and package](../deployment/build-and-package.md)
