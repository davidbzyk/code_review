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

## Architecture notes

* [Context](./context/index.md) - System boundary and entry points.
* [Solution Strategy](./solution-strategy/index.md) - Technologies and structural decisions.
* [Building Blocks](./building-blocks/index.md) - Modules and layers.
* [Runtime](./runtime/index.md) - Step-by-step flows.
* [Deployment](./deployment/index.md) - Build, packaging and CI.
* [Crosscutting](./crosscutting/index.md) - Concerns that span modules.
* [Interfaces](./interfaces/index.md) - Commands, routes and message formats.
* [Glossary](./glossary/index.md) - Terms and their defining files.

## Reserved files

* [Migration Ledger](./MIGRATION_LEDGER.md) - provenance for every source
  document folded into this bundle.
