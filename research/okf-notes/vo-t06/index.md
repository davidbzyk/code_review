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
* [Context](./context/index.md) - What VoiceOver is, who uses it and which outside services it calls.
* [Solution Strategy](./solution-strategy/index.md) - Technologies and structural decisions visible in the code.
* [Building Blocks](./building-blocks/index.md) - One note per layer or module group: responsibility, files, exposed functions, callees.
* [Runtime](./runtime/index.md) - Step by step flows as the code performs them.
* [Deployment](./deployment/index.md) - How the code is built, packaged, tested in automation and started.
* [Crosscutting Concerns](./crosscutting/index.md) - Configuration, secrets, errors, logging, state and testing.
* [Interfaces](./interfaces/index.md) - Boundaries between layers: Tauri commands, events and outside HTTP APIs.
* [Glossary](./glossary/index.md) - Terms used in the code with the file that defines each.

## Reserved files

* [Migration Ledger](./MIGRATION_LEDGER.md) - provenance for every source
  document folded into this bundle.
