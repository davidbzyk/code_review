---
id: building-blocks/orders
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Order totals
description: Orders are summed into a total before checkout.
domain: architecture
tags:
  - orders
  - totals
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/orders.py
related:
  - runtime/checkout-flow
  - crosscutting/logging
---

# Order totals

`compute_total` adds every line price times quantity and returns the order totals.
Totals feed [[runtime/checkout-flow]].
