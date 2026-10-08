---
id: building-blocks/pricing
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Price rules
description: Discount and tax rules applied to a line price.
domain: architecture
tags:
  - pricing
  - discount
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/pricing.py
related:
  - building-blocks/orders
  - runtime/checkout-flow
---

# Price rules

`apply_discount` lowers a line price; `add_tax` raises it. Totals use these rules.
