---
id: MIGRATION_LEDGER
schema: okf/schemas/v1/standard.json
type: Standard
title: Migration Ledger
description: Provenance ledger mapping every source document to its target concept in this bundle.
domain: governance
tags:
  - ledger
  - migration
  - provenance
freshness: "2026-10-06T02:54:48Z"
version: 0.1.0
status: draft
standard_scope: repository-wide
conformance_level: mandatory
governance_body: core-engineering
enforcement: automated-ci
generated:
  by: process:okf_init
  at: "2026-10-06T02:54:48Z"
relations:
  depends_on: []
  relates_to: []
---

# Migration Ledger

Every row maps one source document to what happened to it. `okf_migrate --apply`
appends rows; `okf_verify --docs-dir <dir>` checks that the table covers every
`.md` under that directory.

## Statistics

- **Sources accounted for**: `0`
- **Coverage**: `0.0%`

## Ledger Table

| Source Path | Action | Target | Entity ID | Notes |
|:---|:---|:---|:---|:---|
