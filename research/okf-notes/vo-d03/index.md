---
okf_version: "0.2"
---

# Okf Knowledge Base

An Open Knowledge Format bundle. Every non-reserved `.md` file here is a
concept, and a concept's id is its path within this bundle with `.md` removed.

## Catalogs

* [Architecture Catalog](./architecture/index.md) - System blueprints, runtime execution models, and pipeline specifications.
* [Standards Catalog](./standards/index.md) - Technical contracts, operating conventions, verification protocols, and policies.
* [Domains Catalog](./domains/index.md) - Bounded contexts: one subdirectory per domain, each with its own catalog.
* [Lineage Catalog](./lineage/index.md) - Distilled evidence, inventories, and run history.
* [Tombstones Catalog](./tombstones/index.md) - Records for killed, superseded, or deprecated assets.
* [Schemas Catalog](./schemas/index.md) - The local JSON Schema producer profile and the entity templates.

## Reserved files

* [Migration Ledger](./MIGRATION_LEDGER.md) - provenance for every source
  document folded into this bundle.

## Architecture notes (arc42)

* [context](./context/index.md) - System context and boundary
* [solution-strategy](./solution-strategy/index.md) - Technologies and structural decisions
* [building-blocks](./building-blocks/index.md) - Layers and modules
* [runtime](./runtime/index.md) - Step-by-step flows
* [deployment](./deployment/index.md) - Build, packaging and start
* [crosscutting](./crosscutting/index.md) - Configuration, errors, logging, secrets, state, permissions
* [interfaces](./interfaces/index.md) - Commands, events, HTTP calls, routes
* [glossary](./glossary/index.md) - Terms and defining files
