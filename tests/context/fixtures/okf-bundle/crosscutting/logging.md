---
id: crosscutting/logging
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Logging
description: Structured log lines written by every module.
domain: architecture
tags:
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/log.py
related:

---

# Logging

`log_event` writes one JSON line per event.
