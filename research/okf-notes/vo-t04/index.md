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

## Architecture notes (arc42)

* [Context](./context/index.md) - system boundary and entry points.
* [Solution strategy](./solution-strategy/index.md) - technologies and structural decisions.
* [Building blocks](./building-blocks/index.md) - frontend and Rust modules.
* [Runtime](./runtime/index.md) - step-by-step flows.
* [Deployment](./deployment/index.md) - build, package, start.
* [Cross-cutting](./crosscutting/index.md) - configuration, errors, logging, secrets, state, testing.
* [Interfaces](./interfaces/index.md) - commands, events, HTTP calls, config schema.
* [Glossary](./glossary/index.md) - terms and defining files.

## Reserved files

* [Migration Ledger](./MIGRATION_LEDGER.md) - provenance for every source
  document folded into this bundle.
