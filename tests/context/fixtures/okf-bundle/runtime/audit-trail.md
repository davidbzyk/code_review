---
id: runtime/audit-trail
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Audit trail
description: Who changed which order and when.
domain: architecture
tags:
  - audit
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/audit.py
related:
  - building-blocks/orders
---

# Audit trail

`record_change` appends an audit row.
