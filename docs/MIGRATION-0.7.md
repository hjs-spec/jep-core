# JEP 0.7 Ecosystem Migration

Current Core: **JEP Core 0.7**.

## Current in this repository

- Core 0.7 specification: current/frozen publication.
- Generic schemas: 0.7 current.
- Conformance/02: current published testing conventions; see the [source map](SPECIFICATION-SOURCES.md).
- Profiles/01: 0.7 current draft.
- Python reference validator: 0.7 current.
- 0.7 vectors/manifest: current.
- 0.6 Python/TypeScript/Go validators and vectors: explicit legacy compatibility.

## Cross-repository status

- [JEP-TSTO Binding/02](https://github.com/cognitive-emergence/tsto-spec) is the current TSTO/00 integration for Core 0.7. Its signed marker, typed carriers, pinned joint validation, fixtures and [experimental release](https://github.com/cognitive-emergence/tsto-spec/releases/tag/jep-tsto-binding-02) are maintained in that repository.
- [Software delivery status](https://github.com/hjs-spec/.github/blob/main/DELIVERY-CURRENT.md) tracks API, client and recorder releases separately from package-registry and hosted-deployment status. A protocol version does not imply that every deployment has upgraded.
- [Component format boundaries](architecture/architecture-notes.md#format-and-verification-matrix) identify supported current and historical formats. Preserve each record's original format and signed bytes during migration.
- Application integrations such as Prooftask and semantic/chain profiles require their own explicit compatibility and deployment evidence. Publishing a binding does not migrate their stored history.

## Migration invariants

1. Never rewrite historical 0.6 signatures.
2. Never silently infer 0.6 after a 0.7 failure.
3. Semantic event references use Event Identity.
4. Exact signed-artifact pins continue to use Event Hash.
5. Duplicate delivery is not cryptographic invalidity.
6. Nonce remains allowed where a profile/application actually requires a challenge.
7. Chain, lifecycle, legal, policy, and external truth semantics remain outside Core.
