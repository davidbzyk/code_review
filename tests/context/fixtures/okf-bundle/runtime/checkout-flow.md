---
id: runtime/checkout-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Checkout flow
description: The steps from a filled cart to a paid order.
domain: architecture
tags:
  - checkout
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/checkout.py
related:
  - building-blocks/orders
---

# Checkout flow

Checkout asks orders for the total, then charges the card and writes an audit record.
