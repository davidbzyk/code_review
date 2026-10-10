---
id: interfaces/window-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Window events"
description: "Event names used between the widget page and the main window."
domain: architecture
tags:
  - interfaces
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: interfaces
sources:
  - resource: src/routes/widget/+page.svelte
related:
  - runtime/widget-window-flow
  - building-blocks/route-widget
---

# Window events

The widget page uses Tauri events for control messages.

## Events (src/routes/widget/+page.svelte)
| Name | Direction | Payload |
|---|---|---|
| widget-voice-name | listened | string |
| recording-pause | emitted via invoke of the plugin:event emit command | null |
| recording-resume | emitted via invoke of the plugin:event emit command | null |
| recording-stop | emitted with `emit` | none |
| recording-cancel | emitted with `emit` | none |

## Notes
No `listen` for the four `recording-*` names and no `emit` of `widget-voice-name` appears elsewhere in src/ or src-tauri/src/.

## Related

- [[runtime/widget-window-flow]]
- [[building-blocks/route-widget]]
