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

* [Context](./context/index.md) - System boundary and entry points.
* [Solution strategy](./solution-strategy/index.md) - Technologies and structural decisions.
* [Building blocks](./building-blocks/index.md) - Layers and module groups.
* [Runtime](./runtime/index.md) - Step-by-step flows.
* [Deployment](./deployment/index.md) - Build and packaging.
* [Crosscutting](./crosscutting/index.md) - Configuration, secrets, errors, logging, state, testing.
* [Interfaces](./interfaces/index.md) - Commands, HTTP routes and events.
* [Glossary](./glossary/index.md) - Terms and defining files.
